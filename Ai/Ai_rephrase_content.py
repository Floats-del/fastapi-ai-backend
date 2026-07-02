from utils.APIResponce_error_code_enum import USER_ERROR_CODES, SYSTEM_ERROR_CODES
from typing import Annotated, Any, Literal, Optional
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langsmith import traceable
from pydantic import BaseModel, Field, StringConstraints, field_validator
from Ai.retry_logic import check_provider_quota
from langchain_core.output_parsers import PydanticOutputParser
from core.exceptions import AIServiceException
from utils.logging.logEvents import ProviderLog, RepairLog, SecurityLog, ServiceLog
from utils.schemas import APIResponse
from Ai.intent_classifier import  get_user_intent
from pydantic import ValidationError
from Ai.raw_and_parsed_clean import extract_raw_data, extract_parsed_data
from utils.logging.helper_log import log_state, LogState

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
    )
    
    @field_validator("tone", mode="before") 
    @classmethod
    def normalize_tone(cls, v: Any) -> Any:
        return v.strip().lower() if isinstance(v, str) else v
    
    @field_validator("text", mode="before") 
    @classmethod
    def normalize_text(cls, v: Any) -> Any:
        return v.strip() if isinstance(v, str) else v

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
    log_state(ServiceLog.AI_SERVICE_STARTED, function="rephraser")
    
    if not text or not text.strip():
        log_state(SecurityLog.EMPTY_INPUT, function="rephraser")
        log_state(ServiceLog.AI_SERVICE_FAILED, function="rephraser")
        log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
        return APIResponse(
            success=False,
            data=None,
            error_code=USER_ERROR_CODES.EMPTY_INPUT.value,
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
        log_state(SecurityLog.UNSUPPORTED_INPUT, function="rephraser", exc=e)
        log_state(ServiceLog.AI_SERVICE_FAILED, level=LogState.WARNING, function="rephraser", exc=e)
        log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
        return APIResponse(
            success=False,
            data=None,
            error_code=USER_ERROR_CODES.UNSUPPORTED_INPUT.value,
            error_message=str(e)
        )
    
    intent_package: APIResponse = await get_user_intent(model=llm, text=text)
    if not intent_package.success:
        log_state(ServiceLog.AI_SERVICE_COMPLETED, function="rephraser")
        log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
        return intent_package

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
        log_state(ProviderLog.AI_PROVIDER_REQUEST, function="rephraser") 
        log_state(ProviderLog.AI_PROVIDER_IN_PROCESSING, function="rephraser")
        result = await call_llm(chain, text, tone)
    except Exception as e:
        if check_provider_quota(e):
            log_state(ProviderLog.AI_PROVIDER_FAILURE, level=LogState.EXCEPTION, function="rephraser", exc=e)
            log_state(ServiceLog.AI_SERVICE_FAILED, function="rephraser")
            log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
            return APIResponse(
                success=False,
                data=None,
                error_code=SYSTEM_ERROR_CODES.MY_QUOTA_REACHED.value,
                error_message="No more tokens left to process this request"
            )
        else:
            log_state(ProviderLog.AI_PROVIDER_FAILURE, level=LogState.EXCEPTION, function="rephraser", exc=e)
            log_state(ServiceLog.AI_SERVICE_FAILED, function="rephraser")
            log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
            raise AIServiceException(
                error_code=SYSTEM_ERROR_CODES.AI_SERVICE_FAILURE.value,
                message="AI processing failed during initial generation"
            ) from e
        
    log_state(ProviderLog.AI_PROVIDER_SUCCESS, level=LogState.INFO, function="rephraser")

    parsed = getattr(result, "parsed", None) 
    if parsed is None and isinstance(result, dict):
        parsed = result.get("parsed")

    if isinstance(parsed, dict):
        required_keys = {
            "text",
            "confidence",
            "stylistic_explanation",
            "is_meaning_preserved"
        }

        if not required_keys.issubset(parsed.keys()):
            parsed = None

    if parsed is not None and not isinstance(parsed, (dict, RephraseOutput)):
        parsed = None

    extracted_parsed: RephraseOutput | None = extract_parsed_data(parsed, RephraseOutput) 
    if extracted_parsed:
        log_state(ServiceLog.AI_SERVICE_COMPLETED, function="rephraser")
        log_state(ServiceLog.AI_SERVICE_ENDED, function="rephraser")
        log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
        return APIResponse(
            success=True,
            data=extracted_parsed,
            error_code=None,
            error_message=None
        )

    if extracted_parsed is None:
        log_state(RepairLog.AI_REPAIR_INITIALIZED, function="rephraser")

    raw = getattr(result, "raw", None)
    if raw is None and isinstance(result, dict):
        raw = result.get("raw")

    if raw is None:
        log_state(ServiceLog.AI_SERVICE_FAILED, function="rephraser", level=LogState.WARNING)
        log_state(RepairLog.AI_REPAIR_INITIALIZATION_STOPPED, function="rephraser", level=LogState.WARNING)
        log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser", level=LogState.WARNING)
        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.AI_SERVICE_FAILURE.value,
            error_message="Structured output parsing faild and manual parsing come up empty"
        )
    try:
        log_state(RepairLog.AI_REPAIR_STARTED, function="rephraser")  
        log_state(RepairLog.AI_REPAIR_IN_PROGRESS, function="rephraser") 
        extracted_raw_and_fixed: RephraseOutput | None = await extract_raw_data(raw,parser,llm,text,RephraseOutput)
    except Exception as e:
        if check_provider_quota(e):
            log_state(ServiceLog.AI_MY_QUOTA_REACHED, level=LogState.EXCEPTION, function="rephraser", exc=e)
            log_state(RepairLog.AI_REPAIR_PREMATURELY_ENDED, function="rephraser")    
            log_state(ServiceLog.AI_SERVICE_FAILED, function="rephraser")
            log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")    
            return APIResponse(
                success=False,
                data=None,
                error_code=SYSTEM_ERROR_CODES.MY_QUOTA_REACHED.value,
                error_message="No more tokens left to process this request"
            )
        else:
            log_state(RepairLog.AI_REPAIR_PREMATURELY_ENDED, level=LogState.EXCEPTION, function="rephraser", exc=e)
            log_state(ServiceLog.AI_SERVICE_FAILED, function="rephraser")
            log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
            raise AIServiceException(
                error_code=SYSTEM_ERROR_CODES.AI_SERVICE_FAILURE.value,
                message="AI output recovery process failed"
                ) from e

    if extracted_raw_and_fixed is None:
        log_state(RepairLog.AI_REPAIR_FAILED, function="rephraser")
        log_state(ServiceLog.AI_SERVICE_FAILED, function="rephraser")
        log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.RAW_REPAIR_FAILURE.value, 
            error_message="Structured output parsing failed and manual recovery returned no result."
        )
        
    log_state(RepairLog.AI_REPAIR_SUCCESS, function="rephraser")
    log_state(ServiceLog.AI_SERVICE_COMPLETED, function="rephraser")
    log_state(ServiceLog.AI_SERVICE_ENDED, function="rephraser")
    log_state(ServiceLog.EXITING_AI_SERVICE, function="rephraser")
    return APIResponse(
        success=True,
        data=extracted_raw_and_fixed,
        error_code=None,
        error_message=None
    )