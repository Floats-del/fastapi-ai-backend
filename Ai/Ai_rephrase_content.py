#NOOOOOO MOREEEEE ALTERATION NEEEEDEDDD! (im fully fixed now!)




from typing import Annotated, Any, Literal, Optional
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langsmith import traceable
from pydantic import BaseModel, Field, StringConstraints, field_validator
from Ai.retry_logic import check_provider_quota
from langchain_core.output_parsers import PydanticOutputParser
import json
from core.exceptions import AIServiceException
from utils.schemas import APIResponse
from Ai.intent_classifier import  get_user_intent
from pydantic import ValidationError
from Ai.raw_and_parsed_clean import extract_raw_data, extract_parsed_data
import logging
logger = logging.getLogger(__name__)



#BTW in this case pydentic is not for model to fill member var but for validation of frontend sent data coz if endpoint is hit we only need txt and tone button form front end
class RephraseRequest(BaseModel):
    text: str = Field(..., description="The raw, unformatted text to transform.")
    tone: Literal["rephrase", "professional", "casual", "executive", "simplified", "legal"] = Field(
        default="rephrase",
        description=(
            "- rephrase: Standard cleanup. Fixes grammar, spelling, and clarity while keeping the original tone intact.\n"
            "- professional: Polished, corporate, articulate, and highly engaging. Perfect for LinkedIn.\n"
            "- casual: Conversational, approachable, warm, and friendly. Sounds like a sharp teammate in Slack.\n"
            "- executive: High-level, objective, direct, and incredibly concise. Leads with the bottom line.\n"
            "- simplified: Free of dense jargon. Uses simple analogies so anyone can grasp it immediately.\n"
            "- legal: Highly precise, objective, authoritative, and formal. Minimizes ambiguity."
        )
    ) #tbf since this class is only for validaion i did not rlly had to make it this detailed only text: str, tone: Litera[...] wouldve sufficed
    
    @field_validator("tone", mode="before") 
    @classmethod
    def normalize_tone(cls, v: Any) -> Any:
        # Cleans up incoming tone parameters so messy strings don't trip up the Literal options
        return v.strip().lower() if isinstance(v, str) else v
    
    @field_validator("text", mode="before") 
    @classmethod
    def normalize_text(cls, v: Any) -> Any:
        # Cleans up incoming text parameters safely by only removing trailing whitespace
        return v.strip() if isinstance(v, str) else v





#above one was input validation this is what we want from model!
# This is what we expect the AI model to generate.
class RephraseOutput(BaseModel):
    text: str = Field(
        ...,
        description=(
            "The final rewritten, grammatically optimized version of the input text. "
            "Ensure the core semantic meaning remains completely intact while adapting "
            "the structural tone to the user's specific request."
        )
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Confidence score evaluating the accuracy and semantic alignment of the rewrite from 0.0 to 1.0. "
            "Deduct points if the original meaning was ambiguous, highly corrupted, or structurally difficult to map."
        )
    )
    stylistic_explanation: Annotated[str, StringConstraints(max_length=300, strip_whitespace=True)] = Field(
        ...,
        description=(
            "A clear, brief architectural justification explaining what major grammatical adjustments, "
            "vocabulary alterations, or structural changes were applied to meet the target tone profile."
        )
    )
    is_meaning_preserved: bool = Field(
        default=True,
        description=(
            "Set to False ONLY if the source input text was so severely broken, incoherent, "
            "or self-contradictory that rewriting it forced a speculative change in core meaning."
        )
    )

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:

        return max(0.0, min(v, 1.0))






@traceable(name="initial_llm_call")
async def call_llm(chain, text, tone):
    return await chain.ainvoke({"text": text, "tone": tone})






@traceable(
    name="rephrase_pipeline",
    metadata={"route": "/rephrase"}
)
async def rephraser(llm, text: str, tone: str) -> APIResponse:
    if not text or not text.strip():
        return APIResponse(
            success=False,
            data=None,
            error_code="EMPTY_INPUT",
            error_message="Input text is empty"
        )
    
    try:
        validated_input = RephraseRequest.model_validate(
            {
                "text": text,
                "tone": tone
            }
        )

        text = validated_input.text
        tone = validated_input.tone

    except ValidationError as e:
        return APIResponse(
            success=False,
            data=None,
            error_code="UNSUPPORTED_INPUT",
            error_message=str(e)
        )
    
    
    
    #If ur here form another service read friom be to bellow!
    intent_package: APIResponse = await get_user_intent(model=llm, text=text)
    if not intent_package.success:
        return intent_package #why not return ApiResponce? well get_user_intent gives us api responce so intent_package is the apiresponce!
    #also in get_user_intent, unknown, malicious_injection, is_appropriate(False) result in success=False 
    #so we only continue if we succedded, else APIResponce with what error is given to route!
    #i made get_user_intent return only APIResponce's success=False for all edge cases so no need to check them here
    
    
    #This wont happen now, coz data is only none for each where success=False, and all of those have already been filtered
    """
    actual_intent: IntentUser | None = intent_package.data
    if actual_intent is None:
        return APIResponse(
            success=False,
            data=None,
            error_code="NO_INTENT",
            error_message="Intent classification failed"
        )# why no AiServiceExeption? well coz this is a known error! look we knoe if actual intent is None -> we know!
    """
    
    #no need to check for melishious, injection or appriate coz the where truned away!
    
        
    #READ TOP OF INTENT_CLASSIFIER TO KNOW WHY THIS IS COMMENTED OUT!    
    # if actual_intent.intent != "rephrase" and actual_intent.confidence > 0.85:
    #     logger.info(
    #         f"Expected rephrase, got {actual_intent.intent}"
    #     )
        
    # if actual_intent.intent != "rephrase":
    #     return APIResponse(
    #         success=False,
    #         data=None,
    #         error_code="WRONG_INTENT",
    #         error_message="Request does not match rephrase."
    #     )


    
    
    examples = [
        {
            "input": """
    USER CONTENT:
    hey can you send me the project report by tomorrow? i need it for the meeting.

    REQUESTED TONE:
    professional

    TASK:
    Rewrite the content.
    """,
            "output": """
    {
        "text": "Could you please send me the project report by tomorrow? I need it for the upcoming meeting.",
        "confidence": 0.98,
        "stylistic_explanation": "The message was adjusted with more professional wording, improved sentence structure, and a polite workplace tone while preserving the original request.",
        "is_meaning_preserved": true
    }
    """
        },

        {
            "input": """
    USER CONTENT:
    yo can u check this bug real quick? its annoying me lol

    REQUESTED TONE:
    casual

    TASK:
    Rewrite the content.
    """,
            "output": """
    {
        "text": "Hey, could you check this bug when you get a chance? It's been bothering me.",
        "confidence": 0.97,
        "stylistic_explanation": "The rewrite keeps the informal conversational style while improving grammar and readability.",
        "is_meaning_preserved": true
    }
    """
        },

        {
            "input": """
    USER CONTENT:
    I think we should probably consider maybe improving the database performance because users are experiencing some delays.

    REQUESTED TONE:
    executive

    TASK:
    Rewrite the content.
    """,
            "output": """
    {
        "text": "We should improve database performance to reduce user-facing delays.",
        "confidence": 0.96,
        "stylistic_explanation": "The sentence was shortened and made more direct by removing uncertainty while preserving the business objective.",
        "is_meaning_preserved": true
    }
    """
        },

        {
            "input": """
    USER CONTENT:
    The implementation of asynchronous processing allows the system to handle multiple operations concurrently, improving overall responsiveness.

    REQUESTED TONE:
    simplified

    TASK:
    Rewrite the content.
    """,
            "output": """
    {
        "text": "Using asynchronous processing helps the system handle multiple tasks at the same time, making it faster and more responsive.",
        "confidence": 0.98,
        "stylistic_explanation": "Technical wording was simplified using clearer language while keeping the original technical meaning.",
        "is_meaning_preserved": true
    }
    """
        },

        {
            "input": """
    USER CONTENT:
    You need to submit the documents before the deadline otherwise your application will not be processed.

    REQUESTED TONE:
    legal

    TASK:
    Rewrite the content.
    """,
            "output": """
    {
        "text": "The required documents must be submitted prior to the applicable deadline; otherwise, the application may not be processed.",
        "confidence": 0.97,
        "stylistic_explanation": "The wording was made more formal, precise, and legally structured without changing the original requirement.",
        "is_meaning_preserved": true
    }
    """
        },

        {
            "input": """
    USER CONTENT:
    asdfjkl random words maybe fix this thing somehow

    REQUESTED TONE:
    professional

    TASK:
    Rewrite the content.
    """,
            "output": """
    {
        "text": "The original content is unclear and cannot be reliably rewritten without additional context.",
        "confidence": 0.90,
        "stylistic_explanation": "The input lacked sufficient semantic meaning, making an accurate transformation impossible.",
        "is_meaning_preserved": false
    }
    """
        }]
        
    
    
    template = r"""
    You are a professional backend text-editing engine.

    Your task is to rewrite the text inside the <content> tags according to the requested tone.

    ================ EDITING OBJECTIVE ================

    Transform the provided text while preserving the author's original intent, meaning, and important details.

    Requested tone:
    {tone}

    ================ TRANSFORMATION RULES ================

    1. Correct grammar, spelling, punctuation, and sentence structure.
    2. Improve clarity, readability, and natural flow.
    3. Adjust the writing style to match the requested tone:
    - rephrase: Clean up the text while keeping the original style and meaning.
    - professional: Make it polished, formal, and suitable for workplace communication.
    - casual: Make it friendly, natural, and conversational.
    - executive: Make it concise, direct, and focused on key points.
    - simplified: Make it easier to understand using simpler wording.
    - legal: Make it precise, formal, objective, and unambiguous.

    4. Preserve all factual information exactly:
    - Do not add new information.
    - Do not remove important context.
    - Do not change names, dates, numbers, statistics, URLs, or technical terms.

    5. Preserve formatting-sensitive content:
    - Keep code blocks unchanged.
    - Keep commands, file paths, API names, and technical syntax unchanged.
    - Do not modify quoted text unless required for grammar.

    6. Do not explain your changes.
    Return only the rewritten text.

    ================ INPUT ================

    <content>
    {text}
    </content>
    """
    
    
    structured_model = llm.with_structured_output(RephraseOutput, include_raw=True)
    parser = PydanticOutputParser(pydantic_object=RephraseOutput)
    example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}")
    ])
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            few_shot_prompt,
            ("human","""Rewrite the following user content according to the requested tone:<content>{text}</content>Requested tone:{tone}""")
        ]
    )
    chain = prompt | structured_model
    
    try:
        result = await call_llm(chain, text, tone)

    except Exception as e:
        if check_provider_quota(e):
            return APIResponse(
                success=False,
                data=None,
                error_code="QUOTA_REACHED",
                error_message="No more tokens left to process this request"
            )
        else:
            #new: (but why we raise is same!)
            raise AIServiceException(
                error_code="AI_SERVICE_FAILURE",
                message="AI processing failed during initial generation"
            ) from e #from e carries what origanlly be the exeption type
            
        #old:
        r"""
        #why we raise:
        raise  #why not APIRespocnce? well coz current exception only is used to check for check_provider_quota!
                #when if happens we pass to APIResponse but look in try we have call_llm! which can result in many issues
                    #like AttributeError, ConnectionError etc -> we need these for debugging!
                        #thats why it is imp! but they can halt the system so look new method and go in core folder read why new works!
                            #but trandeoffs of the Api responce contract! --eq(z)
        """

    #parsed: (read in intent_classifer wht i pulled u out)
    parsed = getattr(result, "parsed", None) #the with_structured_output's output
    if parsed is None and isinstance(result, dict):
        parsed = result.get("parsed")

    if isinstance(parsed, dict):
        required_keys = {
            "text",
            "confidence",
            "stylistic_explanation",
            "is_meaning_preserved"
        } #always check for all keys in service schame above class!

        if not required_keys.issubset(parsed.keys()):
            parsed = None
    #we dont exception here! we allow it to fail so things can go into raw's hand!

    if parsed is not None and not isinstance(parsed, (dict, RephraseOutput)):
        parsed = None

    extracted_parsed: RephraseOutput | None = extract_parsed_data(parsed, RephraseOutput) 
    if extracted_parsed:
        # if not validated_intent.is_appropriate:
        #     return APIResponse(
        #         success=False,
        #         data=None,
        #         error_code="INAPPROPRIATE_CONTENT",
        #         error_message="The provided text was flagged as potentially unsafe, a prompt injection, or unreadable."
        #     )
        #NO NEED FOR THIS CHECK COZ WE NOW USE INTENT CLASSIFER TO FILTER INAPPROIATE SUFF OUT AHEAD OF TIME

        #either i get validated obj, or None, if None i send it to raw!
        return APIResponse(
            success=True,
            data=extracted_parsed,
            error_code=None,
            error_message=None
        )
    #parsed dont get a raise we allow it to fail so it can go into manaual



    #raw: (read in inteat_classifer why i pulled it out)
    raw = getattr(result, "raw", None)
    if raw is None and isinstance(result, dict):
        raw = result.get("raw")

    if raw is None:
        return APIResponse(
            success=False,
            data=None,
            error_code="RAW_MISSING",
            error_message="Structured output parsing faild and manual parsing come up empty"
        )
    try:
        extracted_raw_and_fixed: RephraseOutput | None = await extract_raw_data(raw,parser,llm,text,RephraseOutput) #--eq(x) is loaded here and it is in ApiResponce bellow

    except Exception as e: #see  the reason exception is here is coz extract_raw_data calls safe_parse and that calls llm so chace of some other exception is high
        if check_provider_quota(e):
            return APIResponse(
                success=False,
                data=None,
                error_code="QUOTA_REACHED",
                error_message="No more tokens left to process this request"
            )
        
        #if extract_raw_data() throws issue we have this unexpected issue handeler
        raise AIServiceException( #--eq(z) same reason
            error_code="AI_REPAIR_FAILURE",
            message="AI output recovery process failed"
            ) from e



    #if no issues then we move, no issue doesnt mean not None! we gotta check that too
    if extracted_raw_and_fixed is None:
        return APIResponse(
            success=False,
            data=None,
            error_code="RAW_REPAIR_FAILED",
            error_message="Structured output parsing failed and manual recovery returned no result."
        )
    
    return APIResponse(
        success=True,
        data=extracted_raw_and_fixed,
        error_code=None,
        error_message=None
    )