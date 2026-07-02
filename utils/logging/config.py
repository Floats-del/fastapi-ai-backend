import logging

def setup_logging():
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(event)s | %(function)s | %(request_id)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger("ai_saas")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()      # 
    logger.addHandler(handler)
    logger.propagate = False