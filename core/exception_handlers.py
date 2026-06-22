from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.exceptions import AppException
from utils.schemas import APIResponse
import logging
logger = logging.getLogger("uvicorn.error")




#Why i needed this? -> well for success i can return APIResponce where i succedded, but there are cases when idk what exception to send if i just do raise some
#my program can pause there and future code will not execute, since ive excpetion class who inhaits Exception of python and even call said built-in class's 
#member var: messages -> which is the rase Exception("the messge of here") -> now if we we dont know what to do, and dont want sinple raise to halt the app
#i can call this glocabl_exception_handler! as u can see it calls AppException -> which inharits Exception! so all natural exceptions will be auto handeled
#and then wrpaed in APIResponce! and if any other un-identifiecd error comes we got sysmtem error wraped in APIResponce so unexpted is handeled too!
async def global_exception_handler(request: Request, exc: Exception):

    logger.exception(
        "Unhandled application exception"
    )


    if isinstance(exc, AppException):
        response = APIResponse(
            success=False,
            data=None,
            error_code=exc.error_code,
            error_message=exc.message
        )

    else:

        response = APIResponse(
            success=False,
            data=None,
            error_code="SYSTEM_ERROR",
            error_message="Internal server error"
        )


    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(response)
    )


#how to use:
"""
except Exception as e:
    raise AIServiceException(
        "AI_SERVICE_FAILURE",
        "AI processing failed"
    ) from e


we called AIServiceException which inharits form AppException which inhairts form Exception
teachniqally AIServiceException is Exception and in our code1.py ive:

app.add_exception_handler(
    Exception, -> see techiqally huh see!
    global_exception_handler -> the func we wanna run
)

fastapi automatically class this global_exception_handler and passes AIServiceException() exception that we raised in 2nd paramter
and FastAPI already has the request object because it was handling that HTTP request from the beginning.!
so 1st paramter is auto filled!
"""


#NOW WE HAVE WRAPED KNOWN EXCEPTIONS AND UNKNOWN EXCEPTIONS IN gloval_exception_handeler!