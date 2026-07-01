from typing import Any, TypeVar, Type
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import ValidationError
from pydantic import BaseModel
from Ai.retry_logic import safe_parse



T = TypeVar("T", bound=BaseModel)
def extract_parsed_data(parsed: Any, schema: Type[T]) -> T | None:     #when we use with_structure_output(class,raw_output=True) if grentee pydentic object
                                                                    #fails we get raw llm responce like i normally used to get unlike now
                                                                        #so if it works good, if it doesnt ive safe_parse now if it works
                                                                            #if check what does it return a dict? a pydentic (coz structure)
                                                                                #is gurantee but what kind lol this function is basically
                                                                                    #checking which type and making pydentic obj filled with answer
                                                                                        #and return that --eq(1)
                                                                                        
                                                                                        #btw T is <template> for any schma type i pass we done cpp we know  thi
    if parsed is not None:
        if isinstance(parsed, schema):
            return parsed
        if isinstance(parsed, dict):
            try:
                # return IntentUser(**parsed) #same same 
                return schema.model_validate(parsed) #validation and putting gotten data of dict in pydentic obj!
            except ValidationError:     #vaidationError from pydentic only catcues realted errors not python errors, so if we get error we know
                                            #atleast we had issue with pydentic related stuff where early i had Eception: return none meaning no error...

                return None #same case here if we see None bellow we handle it dw
    return None #no need to wrap this in ApiResponce coz extract_parsed_intent() is called in a var and that var is in Apiresponce d!




#as per --eq(1) this one is when struture fails! and i get responce like normal so i gotta check what kind and sent to safe_parse
                                    #with_structure_output -> has 2 things "parsed" and "raw" if we model.with_structured_output(IntentUser, include_raw=True)
                                        #we look into these two keys only! 
#gets data out of what is returned by failed with_structure_output aka extraction form raw
async def extract_raw_data(raw: Any, parser: PydanticOutputParser, model: Any, text: str, schema: type[T]) -> T | None:
    # Handle native tool call extraction variations safely
    if hasattr(raw, "tool_calls") and raw.tool_calls:
        
        for call in raw.tool_calls: #loop coz raw.tool_calls is [too_call1, too_call2] we dont wanna fail if not loop wont run and we process once anyways so no harm
            
            function_data = getattr(call, "function", None)
            
            tool_args = (
                getattr(call, "args", None)
                or (
                    function_data.get("arguments")
                    if isinstance(function_data, dict)
                    else None
                )
                or (
                    call.get("args", {})
                    if isinstance(call, dict)
                    else None
                )
            )

            if isinstance(tool_args, dict) and tool_args:
                try:
                    return schema.model_validate(tool_args)

                except ValidationError:
                    continue

            if isinstance(tool_args, str):
                parsed: T | None = await safe_parse(tool_args, parser, model, text)
                if parsed:
                    return parsed
                else: continue

    # Route raw message text parameters safely into your algorithmic self-healing engine
    if hasattr(raw, "content") and raw.content:
        return await safe_parse(raw.content.strip(), parser, model, text)
        
    if isinstance(raw, str) and raw.strip():
        return await safe_parse(raw, parser, model, text)
    
    return None