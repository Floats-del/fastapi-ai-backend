from utils.logging.logEvents import BaseLogEvent
from utils.logging.logger import (
    log_warning,
    log_info,
    log_error,
    log_exception,
)
from utils.schemas import LogContext
import enum



class LogState(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    EXCEPTION = "exception"
    ERROR = "error"

def log_state(event: BaseLogEvent, level: LogState = LogState.INFO, function: str = "get_user_intent", exc=None):
    ctx = LogContext(
        event=event,
        function=function,
        exception=str(exc) if exc else None,
        exception_type=type(exc).__name__ if exc else None,
    )

    match level:
        case LogState.INFO:
            log_info(ctx)
        case LogState.WARNING:
            log_warning(ctx)
        case LogState.EXCEPTION:
            log_exception(ctx)
        case LogState.ERROR:
            log_error(ctx)