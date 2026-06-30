from utils.logging.logEvents import ExceptionLog


class AppException(Exception):
    """Base exception for application-level errors."""
    # Default fallback log event for any generic app exception
    log_event: ExceptionLog = ExceptionLog.APP_EXCEPTION

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(message)



#later on this when we expand
class AIServiceException(AppException):
    """
    AI related failures.
    """
    # Override the log event specifically for this subclass! (so for each class we have respic )
    log_event: ExceptionLog = ExceptionLog.AI_SERVICE_EXCEPTION



#we can keep adding other classes for diff uses for since each will inahirt AppException which Inharits Excepion so dw