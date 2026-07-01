from utils.schemas import APIResponse
from core.exceptions import AppException
from utils.APIResponce_error_code_enum import SYSTEM_ERROR_CODES


def is_system_failure(result: APIResponse) -> bool:
    return (
        not result.success
        and isinstance(
            result.error_code, #check that result.error_code is instance of SYSTEM_ERROR_CODES! where if go in result.error_code i see error_code=SYSTEM_ERROR_CODES.my_quota_reached, so yes SYSTEM_ERROR_CODES! isinstance!
            SYSTEM_ERROR_CODES
        ) #vr checking for instance! of SYSTEM_ERROR_CODES! not for str! so even if result.error_code is of str type dw!
    )


def handle_service_response(
    result: APIResponse,
    exception_cls: type[AppException] = AppException
):
    if result.success:
        return result.data
    
    raise exception_cls(
        error_code=result.error_code,
        message=result.error_message
    )
"""
Why not JSONResponse? like all other exceptions?
well look exception_cls is of AppException type which calls global_exception_handler which is JSONResponse so ggz
"""
