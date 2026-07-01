from fastapi import Response, status, HTTPException, Depends, APIRouter
from core.exceptions import LikeServiceException
from routers.likes.likes_services import get_logged_in_user_likes_service, liking_post_service
from utils.ai_responce_handler import handle_service_response
from utils.schemas import LikeSchema
from Oauth2 import get_user_jwt_payload
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from db_tables.tables import LikeTable
from utils.schemas import APIResponse
from typing import List

router = APIRouter(
    prefix="/likes",
    tags=['Like']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def like(like_data: LikeSchema, db: AsyncSession = Depends(get_db), user_payload = Depends(get_user_jwt_payload)):
    result: APIResponse = await liking_post_service(like_data=like_data, db=db, user_payload=user_payload)
    return handle_service_response(result, LikeServiceException)



@router.get("/me", response_model=List[int])
async def get_logged_in_user_likes(db: AsyncSession = Depends(get_db), user_payload = Depends(get_user_jwt_payload)):
    """
    Returns a flattened list of post IDs that the currently authenticated user liked.
    Example payload response: [2, 15, 44]
    """
    result: APIResponse = await get_logged_in_user_likes_service(user_payload=user_payload, db=db)
    return handle_service_response(result, LikeServiceException)