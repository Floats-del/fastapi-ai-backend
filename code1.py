import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import db_tables.tables as tables
from db import engine
from routers import posts, users, auth, likes, ai
from core.exception_handlers import global_exception_handler
from utils.config import settings

app = FastAPI(title="Social Network Aggregator API")

app.add_exception_handler(Exception, global_exception_handler)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://10.0.2.2:8000",
    "https://www.yourdomain.com",
    "https://yourdomain.com",
    "https://staging.yourdomain.com",
]

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = settings.api_key
os.environ["LANGCHAIN_PROJECT"] = "fastapi-ai-blog"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=posts.router)
app.include_router(router=users.router)
app.include_router(router=auth.router)
app.include_router(router=likes.router)
app.include_router(router=ai.router)


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Hello World"}