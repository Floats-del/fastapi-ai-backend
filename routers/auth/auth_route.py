from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession 
from core.exceptions import LoginServiceException
from db import get_db
from routers.auth.auth_service import login_user_service
from utils.ai_responce_handler import handle_service_response
from utils.schemas import TokenSchema
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from utils.schemas import APIResponse


router = APIRouter(tags=["Authentication"])

@router.post('/login', response_model=TokenSchema)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> TokenSchema:
    result: APIResponse = await login_user_service(user_credentials=user_credentials, db=db)
    return handle_service_response(result, LoginServiceException)