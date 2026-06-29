import enum


class BaseLogEvent(enum.Enum):
    pass


class AuthLog(BaseLogEvent):

    # ==========================
    # Authentication
    # ==========================
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    JWT_VALIDATION_FAILED = "JWT_VALIDATION_FAILED"




class GatewayLog(BaseLogEvent):

    # ==========================
    # API Gateway
    # ==========================
    AI_REQUEST_RECEIVED = "AI_REQUEST_RECEIVED"
    AI_REQUEST_COLLISION = "AI_REQUEST_COLLISION"
    AI_QUOTA_EXHAUSTED = "AI_QUOTA_EXHAUSTED"




class ReservationLog(BaseLogEvent):

    # ==========================
    # Reservation / Quota
    # ==========================
    AI_RESERVATION_CREATED = "AI_RESERVATION_CREATED"
    AI_RESERVATION_COMPLETED = "AI_RESERVATION_COMPLETED"
    AI_RESERVATION_FAILED = "AI_RESERVATION_FAILED"




class ServiceLog(BaseLogEvent):

    # ==========================
    # AI Service (Your Backend)
    # ==========================
    AI_SERVICE_STARTED = "AI_SERVICE_STARTED"
    AI_SERVICE_IN_PROCESSING = "AI_SERVICE_IN_PROCESSING"
    AI_SERVICE_COMPLETED = "AI_SERVICE_COMPLETED" #comes b4 AI_SERVICE_ENDED in logging
    AI_SERVICE_TERMINATED = "AI_SERVICE_TERMINATED"
    AI_SERVICE_FAILED = "AI_SERVICE_FAILED" #fail due to my 100k issue or genuine issue, or user caused issue
    AI_SERVICE_ENDED = "AI_SERVICE_ENDED" #use this when everything works out and last log is servcice end

    AI_MY_QUOTA_REACHED = "AI_MY_QUOTA_REACHED" #use me if service quta 100k tokens issue happens
    EXITING_AI_SERVICE = "EXITING_AI_SERVICE" #after stop or falure we wanna see this in logs so we knwo request eas out aka next line was 100% retrun
        #termination is also end, but thats force exit!
    """
    context:
    completed -> Business logic succeeded.
    ended -> Service lifecycle finished.
    exiting -> Python is literally leaving the function. (b4 return)

    """



class RepairLog(BaseLogEvent):

    # ==========================
    # Recovery Pipeline
    # ==========================
    AI_REPAIR_INITIALIZED = "AI_REPAIR_INITIALIZED"
    AI_REPAIR_INITIALIZATION_STOPPED = "AI_REPAIR_INITIALIZATION_STOPED" #stop when we end b4 we event went for retry manual loop

    AI_REPAIR_STARTED = "AI_REPAIR_STARTED"
    AI_REPARI_IN_PROGRESS = "AI_REPARI_IN_PROGRESS"
    AI_REPAIR_PREMATURELY_ENDED = "AI_REPAIR_PREMATURELY_ENDED" #end due to some else fail
    AI_REPAIR_SUCCESS = "AI_REPAIR_SUCCESS"
    AI_REPAIR_FAILED = "AI_REPAIR_FAILED"




class ProviderLog(BaseLogEvent):

    # ==========================
    # AI Provider (Groq/OpenAI/etc.)
    # ==========================
    AI_PROVIDER_REQUEST = "AI_PROVIDER_REQUEST"
    AI_PROVIDER_IN_PROCESSING = "AI_PROVIDER_IN_PROCESSING"
    AI_PROVIDER_SUCCESS = "AI_PROVIDER_SUCCESS"
    AI_PROVIDER_FAILURE = "AI_PROVIDER_FAILURE" #then only when llm.inoke cause issue





class DatabaseLog(BaseLogEvent):

    # ==========================
    # Database
    # ==========================
    DB_COMMIT = "DB_COMMIT"
    DB_ROLLBACK = "DB_ROLLBACK"
    DB_ERROR = "DB_ERROR"




class ExceptionLog(BaseLogEvent):

    # ==========================
    # Application Exceptions
    # ==========================
    APP_EXCEPTION = "APP_EXCEPTION"
    AI_SERVICE_EXCEPTION = "AI_SERVICE_EXCEPTION"
    UNHANDLED_EXCEPTION = "UNHANDLED_EXCEPTION"




class SecurityLog(BaseLogEvent):

    # ==========================
    # Security / Content Policy
    # ==========================
    PROMPT_INJECTION_DETECTED = "PROMPT_INJECTION_DETECTED"
    INAPPROPRIATE_CONTENT_DETECTED = "INAPPROPRIATE_CONTENT_DETECTED"
    UNKNOWN_INPUT = "UNKNOWN_INPUT"
    EMPTY_INPUT = "EMPTY_INPUT"
    UNSUPPORTED_INPUT = "UNSUPPORTED_INPUT"


