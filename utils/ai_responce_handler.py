from fastapi import HTTPException, status
from utils.schemas import APIResponse


ERROR_STATUS_MAP = {

    "EMPTY_INPUT": status.HTTP_400_BAD_REQUEST,
    "UNSUPPORTED_INPUT": status.HTTP_400_BAD_REQUEST,

    "PROMPT_INJECTION_DETECTED": status.HTTP_403_FORBIDDEN,
    "INAPPROPRIATE_CONTENT": status.HTTP_403_FORBIDDEN,

    "UNKNOWN_INPUT": status.HTTP_422_UNPROCESSABLE_ENTITY,

    "QUOTA_REACHED": status.HTTP_429_TOO_MANY_REQUESTS,

    "AI_SERVICE_FAILURE": status.HTTP_500_INTERNAL_SERVER_ERROR,
    "AI_REPAIR_FAILURE": status.HTTP_500_INTERNAL_SERVER_ERROR,
    "RAW_REPAIR_FAILED": status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def handle_ai_response(result: APIResponse):

    if result.success:
        return result.data


    raise HTTPException(
        status_code=ERROR_STATUS_MAP.get(
            result.error_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        detail={
            "error_code": result.error_code,
            "message": result.error_message
        }
    )