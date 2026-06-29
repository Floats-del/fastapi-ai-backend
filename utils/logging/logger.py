import logging
from utils.schemas import LogContext
logger = logging.getLogger("ai_saas")

#logging easy via function instead of manual plus logging is also validated via schema
def log_info(context: LogContext):
    logger.info(
        context.event.value,
        extra=context.model_dump(mode="json")
    )

def log_warning(context: LogContext):
    logger.warning(
        context.event.value,
        extra=context.model_dump(mode="json")
    )

def log_error(context: LogContext):
    logger.error(
        context.event.value,
        extra=context.model_dump(mode="json")
    )

def log_exception(context: LogContext):
    logger.exception(
        context.event.value,
        extra=context.model_dump(mode="json")
    )