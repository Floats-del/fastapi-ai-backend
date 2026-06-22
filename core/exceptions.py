class AppException(Exception):
    """
    Base exception for application-level errors.
    """
    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        
        
        
        super().__init__(message)

#why we call super on message?
"""
know that our class inharits Exception class
normal use:
try:
    raise Exception("Database failed")

except Exception as e:
    print(e)

output: Database failed



rn our class has error_code and message member var we can:
exc.error_code
exc.message

to get answers BUT
like in normal use when we raise we do:
raise Exception(str)

but in this calls we would do:

raise AppException(
    "AI_ERROR",
    "Model failed"
)

but rn Exception doesnt know what data was passed in child's class?


super().__init__(message) means:
"Parent Exception, initialize yourself using this message."

coz Exception class intenrally also has member var message we use that one here!
so that member var has all the attributes Exception class had! so in child they're
inharited and now when we pass a message var! and print it we get output
as normal use's example!


to show u how messge var which we inharited would act:
try:
    raise AppException(
        "AI_ERROR",
        "Model failed"
    )

except Exception as e:
    print(e)
    
output: Model failed -> the other didnt came coz it was our custiom we gotta call that ourselvs lol
"""




#later on this when we expand
class AIServiceException(AppException):
    """
    AI related failures.
    """
    pass



#we can keep adding other classes for diff uses for since each will inahirt AppException which Inharits Excepion so dw