from fastapi import status, HTTPException, Depends, APIRouter
from Oauth2 import get_user_jwt_payload
from core.exceptions import UserCreationServiceException
from db_tables.tables import UserTable
from db import get_db
from typing import List, Optional
from routers.users.users_services import create_user_service, get_Nusers_service, get_user_by_id_service
from utils.ai_responce_handler import handle_service_response
from utils.schemas import UserResponseSchema, UserRegisterSchema
from sqlalchemy.ext.asyncio import AsyncSession
from utils.schemas import APIResponse


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def create_user(user: UserRegisterSchema, db: AsyncSession = Depends(get_db)) -> UserResponseSchema:
    result: APIResponse = await create_user_service(user=user, db=db)
    return handle_service_response(result, UserCreationServiceException)


@router.get("/", response_model=List[UserResponseSchema]) 
async def get_all_users(user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db), limit: int = 10, offset: int = 0, search: Optional[str] = None) -> List[UserResponseSchema]: 
    result: APIResponse = await get_Nusers_service(user_payload=user_payload, db=db, limit=limit, offset=offset, search=search)
    return handle_service_response(result, UserCreationServiceException)



@router.get("/{id}", response_model=UserResponseSchema)
async def get_user_by_id(id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):  
    result: APIResponse = await get_user_by_id_service(user_payload=user_payload, db=db, id=id)
    return handle_service_response(result, UserCreationServiceException)
    
    
