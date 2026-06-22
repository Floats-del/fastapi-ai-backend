class AppException(Exception):
    """
    Base exception for application-level errors.
    """
    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        
        
        
        super().__init__(message)



class AIServiceException(AppException):
    """
    AI related failures.
    """
    pass

