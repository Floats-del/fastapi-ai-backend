from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, aliased, joinedload
from sqlalchemy import func
from db_tables.tables import PostTable, LikeTable
from db import get_db
from typing import List, Optional
from utils.schemas import PostLikesOutSchema, PostResponseSchema, PostCreateSchema
from Oauth2 import get_user_jwt_payload
from sqlalchemy.exc import SQLAlchemyError
from db_tables.tables import CommentTable
from utils.schemas import CommentCreateSchema, CommentResponseSchema

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.get("/", response_model=List[PostLikesOutSchema])
def get_all_posts(
    db: Session = Depends(get_db),
    user_payload = Depends(get_user_jwt_payload),
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = None,
    personal_only: bool = False
):
    # Extract the verified user profile information out of the JWT token
    current_user = user_payload.model_dump()
    
    post_alias = aliased(PostTable, name="post") 
    query = db.query(
        post_alias, 
        func.count(LikeTable.post_id).label("likes")
    ).join(
        LikeTable, 
        LikeTable.post_id == post_alias.post_id, 
        isouter=True
    ).group_by(post_alias.post_id)
    
    # Switch between Personal Home page and Discovery Global FYP page
    if personal_only:
        # HOME FEED: Show all of my own creations (including public posts AND private drafts)
        query = query.filter(post_alias.user_id == current_user["user_id"])
    else:
        # FYP FEED: Show global blogs, but ONLY if they are public, and hide my own posts
        query = query.filter(
            post_alias.user_id != current_user["user_id"],
            post_alias.published == True
        )

    if search:
        query = query.filter(post_alias.title.contains(search))

    results = query.offset(offset).limit(limit).all()
    return results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponseSchema) 
def create_post(
    new_post: PostCreateSchema, 
    user_payload = Depends(get_user_jwt_payload),
    db: Session = Depends(get_db)
):
    jwt_payload = user_payload.model_dump()
    post = PostTable(user_id=jwt_payload["user_id"], **new_post.model_dump())    

    try:
        db.add(post)
        db.commit()
        
        # FIX: Eagerly load the user relationship property to avoid missing owner errors
        post_with_owner = db.query(PostTable).options(
            joinedload(PostTable.owner)
        ).filter(PostTable.post_id == post.post_id).first()
        
    except SQLAlchemyError:
        db.rollback() 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database operational failure. Verify data formats and sizes."
        )
    return post_with_owner


@router.get("/{id}", response_model=PostLikesOutSchema)  
def get_post_by_id(
    id: int, 
    user_payload = Depends(get_user_jwt_payload),
    db: Session = Depends(get_db)
):  
    post_alias = aliased(PostTable, name="post") 
    results = db.query(
        post_alias, 
        func.count(LikeTable.post_id).label("likes")
    ).join(
        LikeTable, 
        LikeTable.post_id == post_alias.post_id, 
        isouter=True
    ).filter(
        post_alias.post_id == id
    ).group_by(post_alias.post_id).first()
    
    if not results:
        raise HTTPException(status_code=404, detail="Post Not Found!")
        
    return results



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT) 
def delete_post_by_id(
    id: int, 
    user_payload = Depends(get_user_jwt_payload),
    db: Session = Depends(get_db)
):
    current_user = user_payload.model_dump()
    post = db.query(PostTable).filter(PostTable.post_id == id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found!")
    
    if post.user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized to delete this post!")

    db.delete(post)
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)  


@router.put("/{id}", response_model=PostResponseSchema)
def update_by_id(
    id: int, 
    post_data: PostCreateSchema, 
    user_payload = Depends(get_user_jwt_payload),
    db: Session = Depends(get_db)
):
    current_user = user_payload.model_dump()
    new_data = post_data.model_dump()
    fetched_post = db.query(PostTable).filter(PostTable.post_id == id).first()
    
    if not fetched_post:
        raise HTTPException(status_code=404, detail=f"Post with id: {id} was not found!")
    
    if fetched_post.user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized to Update this post")
    
    for key, value in new_data.items():
        setattr(fetched_post, key, value)

    db.commit()
    
    # FIX: Re-fetch with eager join loading so owner fields match the response model definition
    db.refresh(fetched_post)
    fetched_post = db.query(PostTable).options(
        joinedload(PostTable.owner)
    ).filter(PostTable.post_id == id).first()

    return fetched_post





#no comments create_comment!
@router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED, response_model=CommentResponseSchema)
def create_comment(
    post_id: int,
    comment_data: CommentCreateSchema,
    user_payload = Depends(get_user_jwt_payload),
    db: Session = Depends(get_db)
):
    current_user = user_payload.model_dump()
    
    target_post = db.query(PostTable).filter(PostTable.post_id == post_id).first()
    if not target_post:
        raise HTTPException(status_code=404, detail="Target post does not exist")

    if not target_post.published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot add comments to an unpublished private draft."
        )

    if len(comment_data.text.strip()) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Comment cannot be empty")
    
    new_comment = CommentTable(
        text=comment_data.text,
        user_id=current_user["user_id"],
        post_id=post_id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    comment_with_user = db.query(CommentTable).options(
        joinedload(CommentTable.commenter)
    ).filter(CommentTable.comment_id == new_comment.comment_id).first()
    
    return comment_with_user







@router.get("/{post_id}/comments", response_model=List[CommentResponseSchema])
def get_comments_for_post(
    post_id: int,
    db: Session = Depends(get_db),
    user_payload = Depends(get_user_jwt_payload)
):
    target_post = db.query(PostTable).filter(PostTable.post_id == post_id).first()
    if not target_post:
        raise HTTPException(status_code=404, detail="Target post does not exist")

    comments = db.query(CommentTable).options(
        joinedload(CommentTable.commenter)
    ).filter(CommentTable.post_id == post_id).all()
    
    return comments


@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int,
    comment_id: int,
    user_payload = Depends(get_user_jwt_payload),
    db: Session = Depends(get_db)
):
    current_user = user_payload.model_dump()
    
    comment = db.query(CommentTable).filter(
        CommentTable.comment_id == comment_id,
        CommentTable.post_id == post_id
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if comment.user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment")
        
    db.delete(comment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)