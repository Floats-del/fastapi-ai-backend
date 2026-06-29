from langchain_groq import ChatGroq
from utils.config import settings
from langchain_groq import ChatGroq
from utils.config import settings

model = ChatGroq(
    api_key=settings.api_key,   
    model=settings.model
)

from Ai_rephrase_content import rephraser
from sentiment_analysis import sentiment_analysis
from title_gen import generate_titles
from summry_ai import summry_ai

def print_header(title):
    print(f"\n{'='*25} {title} {'='*25}")

content_sample = (
    "We previously used other tools, but they were slow. FastAPI has proven to be a "
    "better choice because it offers automatic documentation. Additionally, it utilizes "
    "Pydantic, which enables fast type checking, thereby preventing random database crashes. "
    "As a result, our speed has increased significantly."
)

print_header("AI CONTENT REPHRASER")
raw_input = "We used to use other tools but they were slow. FastAPI is good because it has automatic docs. Also it uses pydantic which checks types fast so we don't get random database crashes anymore. Our speed went way up."
print(f"Original Text:\n  \"{raw_input}\"\n")

rephrased = rephraser(model, raw_input)
print(f"Polished Output:\n  \"{rephrased}\"")

print_header("SENTIMENT ANALYSIS ENGINE")
sentiment_input = "Oh! How Bad!, Ive never seen Such A Horendes Blog Before!"
print(f"Target Text: \"{sentiment_input}\"\n")

analysis_result = sentiment_analysis(model, sentiment_input)
print(f"Analysis Breakdown:\n{analysis_result}")

print_header("STRUCTURED TITLE GENERATOR")
print(f"Input Content Summary: {content_sample[:80]}...\n")

titles = []
title_data = generate_titles(model, content_sample)
titles.append(title_data.main_title)
titles.extend(title_data.variations)

print(f"Generated Titles Saved to Array:")
for idx, title in enumerate(titles, 1):
    prefix = f"Main Title:" if idx == 1 else f"Variant {idx-1}:"
    print(f"   {prefix:<12} {title}")

print_header("AI SUMMARY GENERATOR")

summary_result = summry_ai(model, content_sample)
print(f"Executive Summary:\n  {summary_result}")

print(f"\n{'='*68}\n")