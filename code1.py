from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import db_tables.tables as tables
from db import engine
from routers import ai_route\
    
    
from routers.auth import auth_route
from routers.likes import likes_route
from routers.posts import posts_route
from routers.users import users_routes
from utils.logging.config import setup_logging
setup_logging() #called only ONCE! in main


#form docomenration of fastapi CORS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Social Network Aggregator API")


from core.exception_handlers import global_exception_handler, unexpected_exception_handler
from core.exceptions import AppException
app.add_exception_handler(
    AppException, #AppException and all those inharit it, will be handeled by it by:
    global_exception_handler  #this function
)

app.add_exception_handler(
    Exception, #unknown exceptions will be handeld by
    unexpected_exception_handler #this
)



origins = [
    # 1. Vite (React, Vue, Svelte, Tailwind setups)
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # 2. Next.js, Create React App, and Node/Express frontends
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    # 3. Nuxt.js, legacy Vue CLI, and general Webpack setups
    "http://localhost:8080",
    "http://127.0.0.1:8080",

    # 4. Angular default port
    "http://localhost:4200",
    "http://127.0.0.1:4200",

    # 5. Mobile App Emulators (If you build an iOS/Android app later)
    "http://10.0.2.2:8000",  # Android emulator loopback to your local machine

    # 6. Your Production Domains (When you deploy)
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
    CORSMiddleware, #when req comes b4 it can hit any routes it comes to this function!
    allow_origins=origins, #which domains can talk to us, if we want public api we can =["*"]
    allow_credentials=True, 
    #so here is the deal with credentials: When a browser makes a request, it normally strips out things like HTTP 
        #cookies, TLS client certificates, or Authorization headers (like your JWT tokens) for security reasons unless 
            #explicitly told it's allowed. Setting allow_credentials=True tells the browser: "Yes, it is safe to send the
                #user's login tokens and cookies along with the cross-origin request.
                
    allow_methods=["*"], #this rn means all types of request get,post etc! but we can specify which kind of req v accepiting
    allow_headers=["*"], #same for headers
)

app.include_router(router=posts_route.router)
app.include_router(router=users_routes.router)
app.include_router(router=auth_route.router)
app.include_router(router=likes_route.router)
app.include_router(router=ai_route.router)


#normally use this (but in testing ive commented this coz it was returning swagger html TwT)
# @app.get("/", include_in_schema=False)
# def home():
#     return RedirectResponse(url="/docs")


from fastapi import status
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Hello World"}


from dotenv import load_dotenv
load_dotenv()  # This reads the .env file and injects the keys into Python