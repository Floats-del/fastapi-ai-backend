from utils.schemas import APIResponse
from core.exceptions import AppException
from Ai.APIResponce_error_code_enum import SYSTEM_ERROR_CODES


def is_system_failure(result: APIResponse) -> bool:
    return (
        not result.success
        and isinstance(
            result.error_code, #check that result.error_code is instance of SYSTEM_ERROR_CODES! where if go in result.error_code i see error_code=SYSTEM_ERROR_CODES.my_quota_reached, so yes SYSTEM_ERROR_CODES! isinstance!
            SYSTEM_ERROR_CODES
        ) #vr checking for instance! of SYSTEM_ERROR_CODES! not for str! so even if result.error_code is of str type dw!
    )


def handle_ai_response(result: APIResponse):

    if result.success:
        return result.data

    raise AppException( #basically a data filled responce, http code and APIResponce data 
        error_code=result.error_code,
        message=result.error_message
    )