import enum

from pydantic import BaseModel, Field, EmailStr, StringConstraints
from datetime import datetime
from typing import Annotated, Any, Optional, Literal, List, Union

class PostCreateSchema(BaseModel):
    title: str = Field(..., description="Title of the post", max_length=200)
    content: str = Field(..., description="Content of the post", max_length=5000)
    published: bool = Field(True, description="Public visibility status")

class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str

class UserLoginSchema(BaseModel): 
    email: EmailStr
    password: str

class LikeSchema(BaseModel):
    post_id: int
    dir: Literal[0, 1]  

# --- New Comment Payloads ---
class CommentCreateSchema(BaseModel):
    text: str = Field(..., max_length=1000, description="The message content of the comment")

# --- Outgoing Response Layouts ---
class UserResponseSchema(BaseModel):
    email: EmailStr
    user_id: int 
    created_at: datetime
    model_config = {"from_attributes": True}

class PostResponseSchema(PostCreateSchema):
    post_id: int 
    user_id: int 
    owner: UserResponseSchema 
    model_config = {"from_attributes": True} 

class CommentResponseSchema(BaseModel):
    comment_id: int
    post_id: int
    user_id: int
    text: str
    created_at: datetime
    commenter: UserResponseSchema
    model_config = {"from_attributes": True}

class TokenSchema(BaseModel): 
    access_token: str
    token_type: str

class TokenDataSchema(BaseModel): 
    user_id: Optional[int] = None

class PostLikesOutSchema(BaseModel):
    post: PostResponseSchema 
    likes: int 
    model_config = {"from_attributes": True}
"""
from_attributes=True (which was called orm_mode=True in Pydantic v1) allows Pydantic to read ORM models or arbitrary objects (like SQLAlchemy model instances) and turn them into a Pydantic object.
It lets Pydantic extract data from object attributes (using dot notation like user.text) instead of just looking for dictionary keys (like user["text"]).
"""






#AI
#Rephrase-route
class RephraseRequest_route(BaseModel):
    text: Annotated[str, StringConstraints(max_length=3000, strip_whitespace=True)]
    tone: Literal[
        "rephrase",
        "professional",
        "casual",
        "executive",
        "simplified",
        "legal"
    ]

class RephraseOutput_route(BaseModel):
    text: str
    confidence: float
    stylistic_explanation: Annotated[str, StringConstraints(max_length=500, strip_whitespace=True)]
    is_meaning_preserved: bool
    
    model_config = {"from_attributes": True} 





#summary-route:
class SummaryRequest_route(BaseModel):
    text: Annotated[str, StringConstraints(max_length=3000, strip_whitespace=True)]

class SummaryOut_route(BaseModel):
    text: str
    topic: str
    confidence_score: float
    stylistic_explanation: Annotated[str, StringConstraints(max_length=300, strip_whitespace=True)]
    is_meaning_preserved: bool
    model_config = {"from_attributes": True}



#sentiment-route:
class SentimentAnalysisRequest_route(BaseModel):
    text: Annotated[str, StringConstraints(max_length=3000, strip_whitespace=True)]

class SentimentAnalysisOut_route(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed", "casual"]
    confidence_score: float
    explanation: str 
    model_config = {"from_attributes": True}



#title_gem
class Title_genRequest_Route(BaseModel):
    text: Annotated[str, StringConstraints(max_length=3000, strip_whitespace=True)]

class Title_genOut_Route(BaseModel):
    main_title: Union[str, None] 
    variations: List[str] 
    minor_summary: Annotated[str, StringConstraints(max_length=500, strip_whitespace=True)]




#API
#overall server responce
class APIResponse(BaseModel):
    success: bool
    data: Any | None = None #basically the pydentic will be inside it!
    error_code: str | None = None
    error_message: str | None = None




#gateways:
#ai gatways:
class AIGatewayContext(BaseModel):
    user_id: int
    request_id: str




#logging:
#logging schema
from utils.logging.logEvents import BaseLogEvent
class LogContext(BaseModel):
    event: BaseLogEvent #i accept any of said classes child! aka Enum obj of that class! since BaseLogEvent inharits form Enum so ez!

    # Correlation
    request_id: str | None = None
    user_id: int | None = None

    # Location
    route: str | None = None
    function: str | None = None

    # AI
    provider: str = Field(default="groq")
    model: str = Field(
        default="Llama-3.3-70B-Versatile"
    )

    # Performance
    latency_ms: int | None = None

    # Recovery
    repair_used: bool | None = Field(default=False)

    # Errors
    exception: str | None = None
    exception_type: str | None = None #used alongside where we did exception=str(e) then we do exception_type=type(e).__name__
        #where .__name__ tell which kind of exception obj ;)



#helper classes:
#helper class for AiUsageTrackerTable, (what if groq's server down? mine will throw 500 and since as soon as route called due to dependacy user's 24 gone, now 500 form groq and user get nothing) handler
class AIRequestState(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"