from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
from db_tables.tables import UserTable
from utils.APIResponce_error_code_enum import SYSTEM_ERROR_CODES, USER_ERROR_CODES
from utils.hashing import verify_hashed_password
from Oauth2 import create_access_token
from utils.logging.helper_log import LogState, log_state
from utils.logging.logEvents import AuthLogs
from utils.schemas import APIResponse, TokenSchema

async def login_user_service(user_credentials: OAuth2PasswordRequestForm, db: AsyncSession) -> APIResponse:
    log_state(AuthLogs.AUTH_SERVICE_STARTED, function="login_user_service")
    log_state(AuthLogs.AUTHENTICATING_USER, function="login_user_service")

    try:
        log_state(AuthLogs.EXECUTING_DATABASE_QUERY, function="login_user_service")
        result = await db.execute(
            select(UserTable).where(UserTable.email == user_credentials.username)
        )
        fetched_user = result.scalar_one_or_none()

        if not fetched_user:
            log_state(AuthLogs.OPERATION_FAILED, function="login_user_service", level=LogState.WARNING)
            # log_state(AuthLogs.EXITING_AUTH_SERVICE, function="login_user_service")

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message="User not found."
            )

        log_state(AuthLogs.VALIDATING_REQUEST, function="login_user_service", user_id=fetched_user.user_id)

        if not verify_hashed_password(user_credentials.password, fetched_user.password):
            log_state(AuthLogs.OPERATION_FAILED, function="login_user_service", user_id=fetched_user.user_id, level=LogState.WARNING)
            # log_state(AuthLogs.EXITING_AUTH_SERVICE, function="login_user_service")

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNAUTHORIZED_ACCESS.value,
                error_message="Invalid email or password."
            )

        access_token = create_access_token(
            data={"user_id": fetched_user.user_id}
        )
        log_state(AuthLogs.SUCCESS, function="login_user_service", user_id=fetched_user.user_id)

        data = TokenSchema(access_token=access_token, token_type="bearer") #manual validation
        return APIResponse(
            success=True,
            data=data,
            error_code=None,
            error_message=None
        )

    except Exception as e:
        log_state(AuthLogs.OPERATION_FAILED, function="login_user_service", level=LogState.EXCEPTION, exc=e)
        # log_state(AuthLogs.EXITING_AUTH_SERVICE, function="login_user_service") coz finally will always run so no need here

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(AuthLogs.EXITING_AUTH_SERVICE, function="login_user_service")