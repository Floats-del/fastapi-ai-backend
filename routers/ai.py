import enum
import logging
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from Ai.sentiment_analysis import sentiment_analysis_ai
from Ai.title_gen import generate_titles
from Ai.summry_ai import summry_ai
from db import get_db
from Oauth2 import get_user_jwt_payload
from Ai.Ai_rephrase_content import RephraseRequest, rephraser
from Ai.main import model
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from db_tables.tables import AIUsageTrackerTable 
from utils.schemas import AIGatewayContext, AIRequestState, LogContext, LogEvent
from utils.ai_responce_handler import handle_ai_response, is_system_failure

from utils.logging.logger import (
    log_exception,
    log_info,
    log_warning,
    log_error
)
from utils.logging.logEvents import (
    AuthLog,
    DatabaseLog,
    ExceptionLog,
    ReservationLog,
    GatewayLog
)

from utils.schemas import (
    APIResponse,
    RephraseOutput_route,
    RephraseRequest_route,
    SentimentAnalysisOut_route,
    SentimentAnalysisRequest_route,
    SummaryOut_route,
    SummaryRequest_route,
    Title_genOut_Route,
    Title_genRequest_Route,
    TokenDataSchema
)


class QuotaStatus(enum.Enum):
    ALLOWED = "ALLOWED"
    EXHAUSTED = "EXHAUSTED"
    COLLISION = "COLLISION" 


async def consume_ai_quota(db: AsyncSession, user_id: int, request_id: str) -> QuotaStatus:
    now = datetime.now(timezone.utc)
    
    try:
        usage_record = (
            await db.execute(
                select(AIUsageTrackerTable)
                .where(AIUsageTrackerTable.user_id == user_id)
                .with_for_update()
            )
        ).scalar_one_or_none()

        if usage_record is None:
            db.add(
                AIUsageTrackerTable(
                    user_id=user_id,
                    last_used=now,
                    state=AIRequestState.PENDING, 
                    current_request_id=request_id
                )
            )
            await db.commit()
            log_info(
                LogContext(
                    event=ReservationLog.AI_RESERVATION_CREATED,
                    user_id=user_id,
                    request_id=request_id,
                    function="consume_ai_quota"
                )
            )
            return QuotaStatus.ALLOWED

        if usage_record.state == AIRequestState.PENDING:
            await db.rollback()
            log_info(
                LogContext(
                    event=GatewayLog.AI_REQUEST_COLLISION,
                    user_id=user_id,
                    request_id=request_id,
                    function="consume_ai_quota"
                )
            )
            return QuotaStatus.COLLISION 
        
        last_used = usage_record.last_used
        if last_used.tzinfo is None:
            last_used = last_used.replace(
                tzinfo=timezone.utc
            )

        if usage_record.state == AIRequestState.COMPLETED and (now - last_used < timedelta(hours=24)):
            await db.rollback()
            log_info(
                LogContext(
                    event=GatewayLog.AI_QUOTA_EXHAUSTED,
                    user_id=user_id,
                    request_id=request_id,
                    function="consume_ai_quota"
                )
            )
            return QuotaStatus.EXHAUSTED 
        
        usage_record.last_used = now
        usage_record.state = AIRequestState.PENDING
        usage_record.current_request_id = request_id
        await db.commit()

        log_info(
            LogContext(
                event=ReservationLog.AI_RESERVATION_CREATED,
                user_id=user_id,
                request_id=request_id,
                function="consume_ai_quota"
            )
        )
        return QuotaStatus.ALLOWED

    except IntegrityError as e:
        await db.rollback()

        log_info(
            LogContext(
                event=GatewayLog.AI_REQUEST_COLLISION,
                user_id=user_id,
                request_id=request_id,
                function="consume_ai_quota",
                exception=str(e),
                exception_type=type(e).__name__
            )
        )
        return QuotaStatus.COLLISION


async def release_ai_reservation(db: AsyncSession, user_id: int, request_id: str, success: bool) -> None:
    try:
        usage_record = (
            await db.execute(
                select(AIUsageTrackerTable)
                .where(AIUsageTrackerTable.user_id == user_id)
                .with_for_update()
            )
        ).scalar_one_or_none()

        if usage_record is None:
            return

        if usage_record.current_request_id != request_id:
            return

        if success:
            usage_record.state = AIRequestState.COMPLETED 
            log_info(
                LogContext(
                    event=ReservationLog.AI_RESERVATION_COMPLETED, 
                    user_id=user_id,
                    request_id=request_id,
                    function="release_ai_reservation"
                )
            )

        else:
            usage_record.state = AIRequestState.FAILED 

            usage_record.last_used = (
                datetime.now(timezone.utc)
                - timedelta(hours=24)
            )

            log_info(
                LogContext(
                    event=ReservationLog.AI_RESERVATION_FAILED,
                    user_id=user_id,
                    request_id=request_id,
                    function="release_ai_reservation"
                )
            )
        await db.commit()

    except Exception as e:
        await db.rollback()
        log_exception(
            LogContext(
                event=ExceptionLog.APP_EXCEPTION, 
                user_id=user_id,
                request_id=request_id,
                function="release_ai_reservation",
                exception=str(e),
                exception_type=type(e).__name__
            )
        )


async def quota_guard(db: AsyncSession = Depends(get_db), user_payload: TokenDataSchema = Depends(get_user_jwt_payload)):

    current_user: dict = user_payload.model_dump()
    user_id = current_user["user_id"]
    request_id = str(uuid4())

    quota: enum = await consume_ai_quota(db, user_id, request_id)
    
    match quota:
        case QuotaStatus.ALLOWED:
            return {
                "user_payload": user_payload,
                "request_id": request_id
            }
            
        case QuotaStatus.EXHAUSTED:
            raise HTTPException(
                status_code=429,
                detail="Daily AI quota exhausted."
            )

        case QuotaStatus.COLLISION:
            raise HTTPException(
                status_code=409,
                detail="Another AI request is already in progress."
            )


async def ai_gateway(
    quota_data: dict = Depends(quota_guard)
) -> AIGatewayContext:

    return AIGatewayContext(
        user_id=quota_data["user_payload"].user_id,
        request_id=quota_data["request_id"]
    )


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    dependencies=[Depends(get_user_jwt_payload)] 
)


@router.post("/rephrase", response_model=RephraseOutput_route)
async def rephrase_text(
    payload: RephraseRequest_route,
    db: AsyncSession = Depends(get_db),
    quota_guard_data: AIGatewayContext = Depends(ai_gateway) 
) -> RephraseOutput_route:

    request_id = quota_guard_data.request_id
    user_id = quota_guard_data.user_id

    try:
        result: APIResponse = await rephraser(
            model,
            payload.text,
            payload.tone
        )
    
    except Exception:
        await release_ai_reservation(db, user_id, request_id, success=False)
        raise

    await release_ai_reservation( 
        db,
        user_id,
        request_id,
        success = not is_system_failure(result) 
    ) 
    
    return handle_ai_response(result)


@router.post("/summary", response_model=SummaryOut_route)
async def summary_text(payload: SummaryRequest_route,
                       db: AsyncSession = Depends(get_db),
                       quota_guard_data: AIGatewayContext = Depends(ai_gateway)
) -> SummaryOut_route:
    request_id = quota_guard_data.request_id
    user_id = quota_guard_data.user_id
    try:
        result: APIResponse = await summry_ai(
            model, 
            payload.text
        ) 
    except Exception:
        await release_ai_reservation(db, user_id, request_id, success=False)
        raise
    
    await release_ai_reservation(db, user_id, request_id, success= not is_system_failure(result))
    return handle_ai_response(result)


@router.post("/sentiment_analysis", response_model=SentimentAnalysisOut_route)
async def sentiment_analysis(payload: SentimentAnalysisRequest_route, 
                            db: AsyncSession = Depends(get_db),
                            quota_guard_data: AIGatewayContext = Depends(ai_gateway)
) -> SentimentAnalysisOut_route:
    
    request_id = quota_guard_data.request_id
    user_id = quota_guard_data.user_id
    try:
        result: APIResponse = await sentiment_analysis_ai(
            model, 
            payload.text
        ) 
    except Exception:
        await release_ai_reservation(db, user_id, request_id, success=False)
        raise
    
    await release_ai_reservation(db, user_id, request_id, success= not is_system_failure(result))
    return handle_ai_response(result)


@router.post("/title_gen", response_model=Title_genOut_Route)
async def title_gen(payload: Title_genRequest_Route, 
                    db: AsyncSession = Depends(get_db),
                    quota_guard_data: AIGatewayContext = Depends(ai_gateway)
) -> Title_genOut_Route:
    request_id = quota_guard_data.request_id
    user_id = quota_guard_data.user_id
    try:
        result: APIResponse = await generate_titles(
            model, 
            payload.text
        ) 
    except Exception:
        await release_ai_reservation(db, user_id, request_id, success=False)
        raise
    
    await release_ai_reservation(db, user_id, request_id, success= not is_system_failure(result))
    return handle_ai_response(result)