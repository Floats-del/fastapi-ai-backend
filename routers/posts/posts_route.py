from fastapi import status, Depends, APIRouter
from core.exceptions import  PostServiceException
from db import get_db
from typing import List, Optional
from routers.posts.posting_services import create_comment_service, create_post_service, delete_commentById_service, delete_post_by_id_service, fetch_post_by_id, fetch_post_by_id_service, get_Nposts, get_Nposts_service, get_post_comments_service, update_post_by_id_service
from utils.ai_responce_handler import handle_service_response
from utils.schemas import PostLikesOutSchema, PostResponseSchema, PostCreateSchema
from Oauth2 import get_user_jwt_payload
from utils.schemas import APIResponse
from sqlalchemy.ext.asyncio import AsyncSession
from utils.schemas import CommentCreateSchema, CommentResponseSchema





#currently no need for gatway since i only check db and jwt and i need them in routes so itd be pointless
router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)





@router.get("/", response_model=List[PostLikesOutSchema])
async def get_all_posts(db: AsyncSession = Depends(get_db), user_payload = Depends(get_user_jwt_payload), limit: int = 10, offset: int = 0, search: Optional[str] = None, personal_only: bool = False) -> List[PostLikesOutSchema]:
    result: APIResponse = await get_Nposts_service(user_payload=user_payload, db=db, limit=limit, search=search, offset=offset, personal_only=personal_only)
    return handle_service_response(result, PostServiceException) #either i get reult of PostServiceException




@router.post("/", response_model=PostResponseSchema) 
async def create_post(new_post: PostCreateSchema,  user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> PostResponseSchema:
    result: APIResponse = await create_post_service(user_payload=user_payload, db=db, new_post=new_post)
    return handle_service_response(result, PostServiceException)



@router.get("/{id}", response_model=PostLikesOutSchema)  
async def get_post_by_id(id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> PostLikesOutSchema:  
    result: APIResponse = await fetch_post_by_id_service(user_payload=user_payload, db=db, id=id)
    return handle_service_response(result, PostServiceException)





@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_post_by_id(id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await delete_post_by_id_service(user_payload=user_payload, db=db, id=id)
    return handle_service_response(result, PostServiceException)





@router.put("/{id}", response_model=PostResponseSchema)
async def update_by_id(id: int, post_data: PostCreateSchema, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> PostResponseSchema:
    result: APIResponse = await update_post_by_id_service(user_payload=user_payload, db=db, id=id, post_data=post_data)
    return handle_service_response(result, PostServiceException)





#EXPLANATION OF create_comment
"""
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


    if len(comment_data.text) < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Comment cant be empty")
    
    
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
    r"
    db.quert(CommentTable) -> so far db call is not made, we got execution object 
    joinedload(CommentTable.commenter) -> to that excecution object, we add the information to also get
        commenter column, which is relationship("UserTable", back_populates="comments") which is basically
            UserTable orm object why we need it? well coz CommentResponseSchema has commenter: UserResponseSchema
                and UserResponseSchema ->     email: EmailStr, user_id: int, created_at: datetime
                    meaning this:
                    {
                        comment_id: int
                        post_id: int
                        user_id: int
                        text: str
                        created_at: datetime
                        
                        #So far only CommentTable obj will do but for bellow we need relationship stored in 
                            CommentTable.commenter -> ORM obj for UserTable coz it holds feilds like 
                                email, user_id, created_at -> and more but pydentic hides them only shows these
                        
                        commenter: {
                                email: EmailStr
                                user_id: int 
                                created_at: datetime
                            }
                    }
                        since we have what we needed now and more (dw more will be filtred) 
                        when we do .first() -> now db call is made
                        
                        flow:
                        first joinedload(CommentTable.commenter) -> goes and does SELECT * FORM UserTable -> ORM obj
                        then we do SELECT * FROM CommentTable WHERE comment_id = (what_auto_gened)
                        then select it: LIMIT 1;
                        
    now .filter(CommentTable.comment_id == new_comment.comment_id) meaning where CommentTable.comment_id == new_comment.comment_id
    "
    
    
    return comment_with_user #now since we had more that will be filtered
"""


#no comments create_comment!
@router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED, response_model=CommentResponseSchema)
async def create_comment(post_id: int, comment_data: CommentCreateSchema, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> CommentResponseSchema:
    result: APIResponse = await create_comment_service(user_payload=user_payload, post_id=post_id, db=db, comment_data=comment_data)
    return handle_service_response(result, PostServiceException)





@router.get("/{post_id}/comments", response_model=List[CommentResponseSchema])
async def get_comments_for_post(post_id: int, limit: int = 10, offset: int = 0, search: Optional[str] = None, db: AsyncSession = Depends(get_db), user_payload = Depends(get_user_jwt_payload)) -> List[CommentResponseSchema]: 
    result: APIResponse = await get_post_comments_service(user_payload, post_id=post_id, db=db, limit=limit, offset=offset, search=search)
    return handle_service_response(result, PostServiceException)



#the one who left the comments is the one who can delete it!
@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(post_id: int, comment_id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await delete_commentById_service(post_id=post_id, db=db, comment_id=comment_id, user_payload=user_payload)
    return handle_service_response(result, PostServiceException)