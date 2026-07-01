from typing import Optional

from sqlalchemy import select

from db_tables.tables import UserTable
from utils.APIResponce_error_code_enum import SYSTEM_ERROR_CODES, USER_ERROR_CODES
from utils.hashing import hash_password
from utils.logging.helper_log import LogState, log_state
from utils.logging.logEvents import UserLogs
from utils.schemas import  UserRegisterSchema
from utils.schemas import APIResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


async def create_user_service(user: UserRegisterSchema, db: AsyncSession) -> APIResponse:
    log_state(UserLogs.USER_SERVICE_STARTED, function="create_user_service")
    log_state(UserLogs.CREATING_USER, function="create_user_service")

    try:
        log_state(UserLogs.VALIDATING_REQUEST, function="create_user_service")
        hashed_pass = hash_password(user.password)
        new_user = UserTable(
            email=user.email,
            password=hashed_pass
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        log_state(UserLogs.SUCCESS, function="create_user_service", user_id=new_user.user_id)
        return APIResponse(
            success=True,
            data=new_user,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        await db.rollback()
        log_state(
            UserLogs.OPERATION_FAILED,
            function="create_user_service",
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
            UserLogs.OPERATION_FAILED,
            function="create_user_service",
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
        log_state(UserLogs.EXITING_USER_SERVICE, function="create_user_service")

async def get_Nusers_service(user_payload, db: AsyncSession, limit: int = 10, offset: int = 0, search: Optional[str] = None) -> APIResponse:

    log_state(UserLogs.USER_SERVICE_STARTED, function="get_Nusers_service", user_id=user_payload.user_id)
    log_state(UserLogs.FETCHING_USERS, function="get_Nusers_service", user_id=user_payload.user_id)

    try:
        log_state(UserLogs.VALIDATING_REQUEST, function="get_Nusers_service", user_id=user_payload.user_id)

        if limit <= 0:
            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNSUPPORTED_INPUT.value,
                error_message="Limit must be greater than zero."
            )

        if offset < 0:
            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNSUPPORTED_INPUT.value,
                error_message="Offset cannot be negative."
            )

        log_state(UserLogs.EXECUTING_DATABASE_QUERY, function="get_Nusers_service", user_id=user_payload.user_id)
        stmt = select(UserTable)

        if search:
            stmt = stmt.where(
                UserTable.email.contains(search)
            )

        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        users = result.scalars().all()

        log_state(UserLogs.SUCCESS, function="get_Nusers_service", user_id=user_payload.user_id)
        return APIResponse(
            success=True,
            data=users,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        log_state(UserLogs.OPERATION_FAILED, function="get_Nusers_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database query failed."
        )

    except Exception as e:
        log_state(UserLogs.OPERATION_FAILED, function="get_Nusers_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(UserLogs.EXITING_USER_SERVICE, function="get_Nusers_service", user_id=user_payload.user_id)
        
async def get_user_by_id_service(user_payload, id: int, db: AsyncSession) -> APIResponse:
    log_state(UserLogs.USER_SERVICE_STARTED, function="get_user_by_id_service", user_id=user_payload.user_id)
    log_state(UserLogs.FETCHING_USER, function="get_user_by_id_service", user_id=user_payload.user_id)

    try:
        log_state(UserLogs.EXECUTING_DATABASE_QUERY, function="get_user_by_id_service", user_id=user_payload.user_id)
        result = await db.execute(
            select(UserTable).where(UserTable.user_id == id)
        )
        fetched_user = result.scalar_one_or_none()

        if not fetched_user:
            log_state(UserLogs.OPERATION_FAILED, function="get_user_by_id_service", user_id=user_payload.user_id, level=LogState.WARNING)

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message="User not found."
            )

        log_state(UserLogs.SUCCESS, function="get_user_by_id_service", user_id=user_payload.user_id)
        return APIResponse(
            success=True,
            data=fetched_user,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        log_state(UserLogs.OPERATION_FAILED, function="get_user_by_id_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database query failed."
        )

    except Exception as e:
        log_state(UserLogs.OPERATION_FAILED, function="get_user_by_id_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(UserLogs.EXITING_USER_SERVICE, function="get_user_by_id_service", user_id=user_payload.user_id)