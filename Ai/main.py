#& G:\python\G_Env\Scripts\python.exe "g:/python/BackEnd FastAPI/Lecs/L17/Ai/main.py"
from langchain_groq import ChatGroq
from utils.config import settings
from langchain_groq import ChatGroq
from utils.config import settings

# Initialize Model
model = ChatGroq(
    api_key=settings.api_key,   
    model=settings.model
)

# Imports
from Ai_rephrase_content import rephraser
from sentiment_analysis import sentiment_analysis
from title_gen import generate_titles
from summry_ai import summry_ai

# UI Styling Helpers (ANSI Escape Codes for Terminal Colors)
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(title, color):
    print(f"\n{color}{BOLD}{'='*25} {title} {'='*25}{RESET}")

content_sample = (
    "We previously used other tools, but they were slow. FastAPI has proven to be a "
    "better choice because it offers automatic documentation. Additionally, it utilizes "
    "Pydantic, which enables fast type checking, thereby preventing random database crashes. "
    "As a result, our speed has increased significantly."
)

# ---------------------------------------------------------
# 1. Content Rephraser
# ---------------------------------------------------------
print_header("AI CONTENT REPHRASER", GREEN)
raw_input = "We used to use other tools but they were slow. FastAPI is good because it has automatic docs. Also it uses pydantic which checks types fast so we don't get random database crashes anymore. Our speed went way up."
print(f"{BOLD}Original Text:{RESET}\n  \"{raw_input}\"\n")

rephrased = rephraser(model, raw_input)
print(f"{BOLD}Polished Output:{RESET}\n  \"{rephrased}\"")


# ---------------------------------------------------------
# 2. Sentiment Analysis
# ---------------------------------------------------------
print_header("SENTIMENT ANALYSIS ENGINE", CYAN)
sentiment_input = "Oh! How Bad!, Ive never seen Such A Horendes Blog Before!"
print(f"{BOLD}Target Text:{RESET} \"{sentiment_input}\"\n")

analysis_result = sentiment_analysis(model, sentiment_input)
print(f"{BOLD}Analysis Breakdown:{RESET}\n{analysis_result}")


# ---------------------------------------------------------
# 3. Title Generation (Structured Pydantic Data)
# ---------------------------------------------------------
print_header("STRUCTURED TITLE GENERATOR", YELLOW)
print(f"{BOLD}Input Content Summary:{RESET} {content_sample[:80]}...\n")

titles = []
title_data = generate_titles(model, content_sample)
titles.append(title_data.main_title)
titles.extend(title_data.variations)

print(f"{BOLD}Generated Titles Saved to Array:{RESET}")
for idx, title in enumerate(titles, 1):
    prefix = f"{BOLD}Main Title:{RESET}" if idx == 1 else f"Variant {idx-1}:"
    print(f"  📌 {prefix:<12} {title}")


# ---------------------------------------------------------
# 4. Blog Summary Generation
# ---------------------------------------------------------
print_header("AI SUMMARY GENERATOR", MAGENTA)

summary_result = summry_ai(model, content_sample)
print(f"{BOLD}Executive Summary:{RESET}\n  {summary_result}")

print(f"\n{BOLD}{'='*68}{RESET}\n")