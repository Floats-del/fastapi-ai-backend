#1) when we await something our controll can go and do other stuff and wait for the awiting thing to finish 
#2) uvicorn main:app --workers 4 -> we get 4 workers meaning 4 event loops parallel (just like game dev while loop)
#3) say ive 100 users 4 worksers then each workr get 25 users each -> load balancers
#4) now how does async and await comes into ply? as per point(3) 1 worker can have more than 1 user
#5) lets go by that woker 1 (process) has 25 users in same event loop, say user x came first and asked for rephrase
    #without the await rest of the 24 will have to wait a bit till content_swithcing(process either finishes or intruped b4 next gets a chace) will happen
        #(they still will get cpu a lil late tho)... imagien if await was there they'd've saved some seconds and context_switch wouldve happend be return or an intrupt 
            #now if we do await if persion x askes #for rephrase instead of wait till work finishes, worker will make user x wait for rephrase to finish while it tends to 
                #the next person who made request after person x! and do his stuff 
                    #event loop is constantly switching with tasks (just like we red in scheduling alogs in OS)
                        #so no idel time! await is when the wait_time is huge! so instead of delay in switch we ANNOUNCE a paue for that person
                            #switching is always happening!


from langsmith import traceable
from langchain_core.exceptions import OutputParserException 
from typing import List




# logger = logging.getLogger("uvicorn.error") used in routes
def is_provider_limit_error(exception: Exception) -> bool:
    """
    Scans the exception message to see if the upstream AI provider 
    (Ollama, HuggingFace, OpenAI, etc.) has run out of tokens or hit rate limits.
    """
    err_msg = str(exception).lower()
    limit_keywords = [
        "insufficient_quota", 
        "rate_limit_exceeded", 
        "token_limit_exceeded", 
        "quota exceeded", 
        "429", 
        "out of tokens"
    ]
    return any(keyword in err_msg for keyword in limit_keywords)


def check_provider_quota(exception: Exception) -> bool:
    """
    Returns True if AI provider quota/rate limit issue happened.
    """
    return is_provider_limit_error(exception)




def clean_json_string(raw_str):
    # Find the first '{' and the last '}'
    start_idx = raw_str.find('{')
    end_idx = raw_str.rfind('}')
    
    if start_idx == -1 or end_idx == -1:
        return raw_str # Fallback
    return raw_str[start_idx:end_idx + 1]





#MY OWN PARSER ONE! WHICH GOT DECRYPTED AND I MADE MY OWN! (and the only one i use and call in raw_and_parsed_clean's raw recovery)
@traceable(name="safe_parse_3Retry_one")
async def safe_parse(raw_output, parser, llm, query, max_retries=3) -> object | None:
    #we do 3 tries OutputFixingParser used to once!
    output = raw_output # we keep updating this untill it passes our checks! aka we safely return our class pydantic obj!

    for attempt in range(max_retries):

        #check of the model output is AIMessage or nah
        # important: handle HF message objects
        current_str = output.content if hasattr(output, "content") else output  
        #hasattr -> check if in output we have .contnet attribute which is inside AIMessage meaning we didnt get json str rather AIMessage obj!        
        current_str = str(current_str).strip()


        # Remove markdown junk
        if "```" in current_str:
            parts: List[str] = current_str.split("```")
            current_str = max(parts, key=len).strip()
            
            
            if current_str.lower().startswith("json"):
                current_str = current_str[4:].strip() #j s o n, 4 words! we reomve it too! (MAKE SAPRATE FUNC FOR THIS GNG!)
                
            current_str = clean_json_string(current_str)

        try:
            return parser.parse(current_str) #in OutputFixingParser this used to happen ineternally! and it returns a pydentic object!
            #if after parsing aka checking if model output is same as our class schema then return coz we achived!
            #which object u may ask? well when we send parser we make parser as: parser = PydanticOutputParser(pydantic_object=TitlePackage)
            #so whicever type is parser that type of obj with all its member var filled as per class will be returned!
            
            """
            Something like this:
                {
                "complexity": "normal",
                "confidence": 0.92,
                "explanation": "Simple select query",
                "requires_decomposition": false
                }
            """

        except OutputParserException as e: #normally OutputFixingParser uses to throw this OutputParserException excpetion now we manually!
            if attempt == max_retries - 1:
                # last attempt failed -> no valid pydantic object can be created
                return None

            repair_prompt = f"""
            You MUST return valid JSON only.
            NO text.
            NO explanation.
            NO markdown blocks.

            Target Format Instructions:
            {parser.get_format_instructions()}

            Context/Task Being Evaluated:
            {query}

            Broken Target String:
            {current_str}

            Parser Parsing Error Encountered:
            {e}

            Fix the JSON formatting error above and return a fully compliant object matching the target format instructions exactly.
            """
            try:
                output = await llm.ainvoke(repair_prompt)
                #Changed to await llm.ainvoke() to release the FastAPI event loop!

            except Exception as e:
                if check_provider_quota(e):
                    return None
                    
    #all retries exhausted and no valid pydantic object was produced
    return None










# #RE-TRY REPHRASE ONE.. IF REPHRASE IS BAD! (im pretty sure safe_parse now can do what this does too lol!) [to that end this is not standarized!]
# @traceable(name="safe_text_generation")
# async def safe_text_generation(raw_output, llm, prompt_context, max_retries=3):
#     """
#     A parser-free self-healing loop for regular text generation.
#     Ensures the output isn't empty, clears unwanted markdown syntax, and retries if broken.
#     """
#     output = raw_output

#     for attempt in range(max_retries):
#         # 1. Extract raw text from the LLM response structure safely
#         current_str = output.content if hasattr(output, 'content') else output
#         current_str = str(current_str).strip()

#         # 2. Heuristic Check: Did the model hallucinate and wrap a normal text paragraph in markdown fences?
#         if current_str.startswith("```"):
#             # Strip out markdown block indicators if the user just wanted a clean sentence
#             parts = current_str.split("```")
#             current_str = max(parts, key=len).strip()
#             if current_str.lower().startswith("text"):
#                 current_str = current_str[4:].strip()

#         # 3. Custom Evaluation Rules (Add whatever validation rules you want here)
#         is_valid = True
#         error_reason = ""

#         if not current_str:
#             is_valid = False
#             error_reason = "The response is completely empty."
        
#         # Example check: Ensure it didn't just spit out a generic system error message
#         if "as an ai language model" in current_str.lower():
#             is_valid = False
#             error_reason = "The model returned a generic refusal statement instead of processing the text."

#         # 4. Loop Resolution or Repair Trigger
#         if is_valid:
#             return current_str

#         if attempt == max_retries - 1:
#             raise ValueError(f"Text generation failed validation permanently: {error_reason}")

#         # 5. Build a text-specific repair query
#         repair_prompt = f"""
#         Your previous response failed validation rules. Please correct the output immediately.
        
#         Reason for Failure: {error_reason}
        
#         Original Context/Task:
#         {prompt_context}
        
#         Broken Output to fix:
#         {current_str}
        
#         Return ONLY the final, clean, corrected text output.
#         """
#         try:
#             # Upstream call to fix empty generation or refusal statements
#             output = await llm.ainvoke(repair_prompt)
#         except Exception as invoke_err:
#             if is_provider_limit_error(invoke_err):
#                 logger.error(f"Upstream AI Provider Quota Blown during text repair: {invoke_err}")
#                 raise RuntimeError("The global AI core pool has reached its processing limit.")
#             raise invoke_err

#     raise ValueError("Text generation self-repair loop failed.")