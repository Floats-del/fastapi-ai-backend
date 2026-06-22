from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from Ai import sentiment_analysis_ai
from Ai.title_gen import generate_titles
from Ai.summry_ai import summry_ai
from db import get_db
from Oauth2 import get_user_jwt_payload
from Ai.Ai_rephrase_content import RephraseRequest, rephraser
from Ai.main import model
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from db_tables.tables import AIUsageTrackerTable 
from utils.ai_responce_handler import handle_ai_response
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

async def consume_ai_quota(db: AsyncSession, user_id: int) -> bool:
    now = datetime.now(timezone.utc)
    
    try:
        usage_record = (await db.execute(
            select(AIUsageTrackerTable)
            .where(AIUsageTrackerTable.user_id == user_id)
            .with_for_update()
        )).scalar_one_or_none()
        
        if usage_record is None:
            db.add(
                AIUsageTrackerTable(
                    user_id=user_id,
                    last_used=now
                )
            )
            await db.commit()
            return True

        last_used = usage_record.last_used

        if last_used.tzinfo is None:
            last_used = last_used.replace(
                tzinfo=timezone.utc
            )

        if now - last_used < timedelta(hours=24):
            await db.rollback()
            return False

        usage_record.last_used = now
        await db.commit()
        return True

    except IntegrityError:
        await db.rollback()
        return False

async def ai_gateWay(
    db: AsyncSession = Depends(get_db),
    user_payload = Depends(get_user_jwt_payload)
): 
    current_user = user_payload.model_dump()
    user_id = current_user["user_id"]
    quota_secured = await consume_ai_quota(db, user_id) 
        
    if not quota_secured:
        raise HTTPException(
            status_code=429,
            detail="AI quota exhausted or request collision. Try again later."
        )
    return user_payload

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    dependencies=[Depends(ai_gateWay)]
)

@router.post("/rephrase", response_model=RephraseOutput_route) 
async def rephrase_text(payload: RephraseRequest_route, 
                        user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload), 
                        db: AsyncSession = Depends(get_db)):
    result: APIResponse = await rephraser(
        model,
        payload.text,
        payload.tone
    )
    
    responce: RephraseRequest = handle_ai_response(result)
    return responce

@router.post("/summary", response_model=SummaryOut_route)
async def summary_text(payload: SummaryRequest_route,
                       user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload),
                       db: AsyncSession = Depends(get_db)
                       ):
    result: APIResponse = await summry_ai(
        model, 
        payload.text
    ) 
    
    return handle_ai_response(result)

@router.post("/sentiment_analysis", response_model=SentimentAnalysisOut_route)
async def sentiment_analysis(payload: SentimentAnalysisRequest_route, user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await sentiment_analysis_ai(
        model,
        payload.text
    )
    return handle_ai_response(result)

@router.post("/title_gen", response_model=Title_genOut_Route)
async def title_gen(payload: Title_genRequest_Route, user_jwt_payload: TokenDataSchema = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await generate_titles(
        model,
        payload.text
    )
    return handle_ai_response(result)