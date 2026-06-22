from fastapi import Response, status, HTTPException, Depends, APIRouter
from utils.schemas import LikeSchema
from Oauth2 import get_user_jwt_payload
from db import get_db
from sqlalchemy.orm import Session
from db_tables.tables import LikeTable, PostTable
from typing import List

router = APIRouter(
    prefix="/likes",
    tags=['Like']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def like(like_data: LikeSchema, db: Session = Depends(get_db), 
         user_payload = Depends(get_user_jwt_payload)):
         
    # Validate destination target post entity actively exists in database
    found_post = db.query(PostTable).filter(PostTable.post_id == like_data.post_id).first()
    
    if not found_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user has already assigned relationship structures to this record 
    found_like = db.query(LikeTable).filter(
        LikeTable.post_id == like_data.post_id, 
        LikeTable.user_id == user_payload.user_id
    ).first()

    if like_data.dir == 1: 
        if found_like: 
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already liked...")
        
        new_like = LikeTable(post_id=like_data.post_id, user_id=user_payload.user_id)
        db.add(new_like)
        db.commit()
        return Response(status_code=status.HTTP_200_OK)  
    
    else: # Operation: Unlike post (dir=0)
        if not found_like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Like does not exist, try liking the post before unliking..."
            )
        
        db.delete(found_like)
        db.commit()
        return Response(status_code=status.HTTP_200_OK)


@router.get("/me", response_model=List[int])
def get_logged_in_user_likes(
    db: Session = Depends(get_db), 
    user_payload = Depends(get_user_jwt_payload)
):
    """
    Returns a flattened list of post IDs that the currently authenticated user liked.
    Example payload response: [2, 15, 44]
    """
    current_user = user_payload.model_dump()
    
    # Query only the post_id column to keep database performance blazing fast
    liked_post_ids = db.query(LikeTable.post_id).filter(
        LikeTable.user_id == current_user["user_id"]
    ).all()
    
    # Flatten the SQLAlchemy list of tuples (e.g., [(2,), (15,)]) into a list of ints
    return [post_id[0] for post_id in liked_post_ids]