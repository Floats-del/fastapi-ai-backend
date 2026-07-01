from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db_tables.tables import LikeTable, PostTable

from utils.APIResponce_error_code_enum import SYSTEM_ERROR_CODES, USER_ERROR_CODES
from utils.logging.helper_log import LogState, log_state
from utils.logging.logEvents import LikeLogs
from utils.schemas import APIResponse, LikeSchema


async def liking_post_service(user_payload, like_data: LikeSchema, db: AsyncSession) -> APIResponse:
    log_state(LikeLogs.LIKE_SERVICE_STARTED, function="liking_post_service", user_id=user_payload.user_id)

    operation_log = LikeLogs.LIKING_POST if like_data.dir == 1 else LikeLogs.UNLIKING_POST
    log_state(operation_log, function="liking_post_service", user_id=user_payload.user_id)

    try:
        log_state(LikeLogs.EXECUTING_DATABASE_QUERY, function="liking_post_service", user_id=user_payload.user_id)
        result = await db.execute(
            select(PostTable).where(PostTable.post_id == like_data.post_id)
        )

        found_post = result.scalar_one_or_none()
        if not found_post:
            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message="Post not found."
            )

        result = await db.execute(
            select(LikeTable).where(
                LikeTable.post_id == like_data.post_id,
                LikeTable.user_id == user_payload.user_id
            )
        )
        found_like = result.scalar_one_or_none()
        
        if like_data.dir == 1:
            if found_like:
                return APIResponse(
                    success=False,
                    data=None,
                    error_code=USER_ERROR_CODES.DUPLICATE_RESOURCE.value,
                    error_message="You have already liked this post."
                )

            new_like = LikeTable(
                post_id=like_data.post_id,
                user_id=user_payload.user_id
            )

            db.add(new_like)
            await db.commit()

        else:
            if not found_like:
                return APIResponse(
                    success=False,
                    data=None,
                    error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                    error_message="Like does not exist."
                )

            await db.delete(found_like)
            await db.commit()

        log_state(LikeLogs.SUCCESS, function="liking_post_service", user_id=user_payload.user_id)
        return APIResponse(
            success=True,
            data=None,
            error_code=None,
            error_message=None
        )


    except SQLAlchemyError as e:
        await db.rollback()

        log_state(
            LikeLogs.OPERATION_FAILED,
            function="liking_post_service",
            user_id=user_payload.user_id,
            level=LogState.ERROR,
            exc=e
        )

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database operation failed."
        )


    except Exception as e:
        await db.rollback()

        log_state(
            LikeLogs.OPERATION_FAILED,
            function="liking_post_service",
            user_id=user_payload.user_id,
            level=LogState.EXCEPTION,
            exc=e
        )

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(
            LikeLogs.EXITING_LIKE_SERVICE,
            function="liking_post_service",
            user_id=user_payload.user_id
        )



async def get_logged_in_user_likes_service(user_payload, db: AsyncSession) -> APIResponse:
    log_state(LikeLogs.LIKE_SERVICE_STARTED, function="get_logged_in_user_likes_service", user_id=user_payload.user_id)
    log_state(LikeLogs.FETCHING_USER_LIKES, function="get_logged_in_user_likes_service", user_id=user_payload.user_id)

    try:
        log_state(LikeLogs.EXECUTING_DATABASE_QUERY, function="get_logged_in_user_likes_service", user_id=user_payload.user_id)

        result = await db.execute(
            select(LikeTable.post_id).where(
                LikeTable.user_id == user_payload.user_id
            )
        )

        liked_post_ids = result.scalars().all()
        log_state(LikeLogs.SUCCESS, function="get_logged_in_user_likes_service", user_id=user_payload.user_id)

        return APIResponse(
            success=True,
            data=liked_post_ids,
            error_code=None,
            error_message=None
        )


    except SQLAlchemyError as e:
        await db.rollback()

        log_state(
            LikeLogs.OPERATION_FAILED,
            function="get_logged_in_user_likes_service",
            user_id=user_payload.user_id,
            level=LogState.ERROR,
            exc=e
        )

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database query failed."
        )


    except Exception as e:
        await db.rollback()

        log_state(
            LikeLogs.OPERATION_FAILED,
            function="get_logged_in_user_likes_service",
            user_id=user_payload.user_id,
            level=LogState.EXCEPTION,
            exc=e
        )

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(
            LikeLogs.EXITING_LIKE_SERVICE,
            function="get_logged_in_user_likes_service",
            user_id=user_payload.user_id
        )