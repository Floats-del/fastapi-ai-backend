import enum 
class USER_ERROR_CODES(enum.Enum):
    EMPTY_INPUT = "EMPTY_INPUT"
    UNSUPPORTED_INPUT = "UNSUPPORTED_INPUT"
    PROMPT_INJECTION_DETECTED = "PROMPT_INJECTION_DETECTED"
    INAPPROPRIATE_CONTENT = "INAPPROPRIATE_CONTENT"
    UNKNOWN_INPUT = "UNKNOWN_INPUT"
    
    
    #auth:
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    
    
    #service:
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"

class SYSTEM_ERROR_CODES(enum.Enum):
    #Ai related:
    MY_QUOTA_REACHED = "MY_QUOTA_REACHED"
    AI_SERVICE_FAILURE = "AI_SERVICE_FAILURE"
    AI_REPAIR_FAILURE = "AI_REPAIR_FAILURE" #for parcer but we let it fail (coz we allow fail, so we wont use this to raise an exception)
    RAW_REPAIR_FAILURE = "RAW_REPAIR_FAILURE"

    #App realted:
    
    
    
    #DB related:
    DATABASE_ERROR = "DATABASE_ERROR"
    
    
    #system:
    UNKNOWN_ERROR = "UNKNOWN_ERROR"