#new:
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse



from core.exceptions import AppException
from core.error_registery import ERROR_STATUS_MAP
from utils.schemas import APIResponse


from utils.schemas import LogContext
from utils.logging.logger import (
    log_exception
)

from utils.logging.logEvents import ExceptionLog
from Ai.helper_log import log_state, LogState



async def global_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    
    # Safely get the specific log event from the exception instance
    current_log_event: ExceptionLog = getattr(exc, "log_event", ExceptionLog.APP_EXCEPTION) 
    log_state(current_log_event, level=LogState.EXCEPTION, function="global_exception_handler", route=str(request.url.path), exc=exc)
        
    
    response = APIResponse(
        success=False,
        data=None,
        error_code=exc.error_code, #dw when i raise custom excption i do .value there, so here it will come out as str anyways
        error_message=exc.message
    )

    return JSONResponse(#btw this returns a json http responce! so we can raise an exception with data ;)
        status_code=ERROR_STATUS_MAP.get( #get arg .get(x if not find make the caller y)
            exc.error_code, #get this 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        content=jsonable_encoder(response) #see im injecting APIResonce data into http responce ;)
    )


async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log_state(ExceptionLog.UNHANDLED_EXCEPTION, level=LogState.EXCEPTION, function="unexpected_exception_handler", route=str(request.url.path), exc=exc)

    response = APIResponse(
        success=False,
        data=None,
        error_code="SYSTEM_ERROR", #vr doing system error here coz, this is genral Eception which we dont know either lol
        error_message="Internal server error"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(response)
    )