from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import db_tables.tables as tables
from db import engine
from routers import posts, users, auth, likes, ai\
    
    
from utils.logging.config import setup_logging
setup_logging() 


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Social Network Aggregator API")


from core.exception_handlers import global_exception_handler, unexpected_exception_handler
from core.exceptions import AppException
app.add_exception_handler(
    AppException, 
    global_exception_handler  
)

app.add_exception_handler(
    Exception, 
    unexpected_exception_handler 
)



origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    "http://localhost:3000",
    "http://127.0.0.1:3000",

 
    "http://localhost:8080",
    "http://127.0.0.1:8080",

    "http://localhost:4200",
    "http://127.0.0.1:4200",

    "http://0.0.2.2:8000",  

    "https://www.yourdomain.com",
    "https://yourdomain.com",
    "https://staging.yourdomain.com",
]
from utils.config import settings
import os
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






from fastapi import status
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Hello World"}


from dotenv import load_dotenv
load_dotenv()