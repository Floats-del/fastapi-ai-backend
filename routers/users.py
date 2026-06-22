from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from Oauth2 import get_user_jwt_payload
from db_tables.tables import UserTable
from db import get_db
from typing import List
from utils.hashing import hash_password
from utils.schemas import UserResponseSchema, UserRegisterSchema

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
def create_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    hashed_pass = hash_password(user.password)
    new_user = UserTable(email=user.email, password=hashed_pass)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=List[UserResponseSchema]) 
def get_all_users(
    user_payload = Depends(get_user_jwt_payload),
    db: Session = Depends(get_db)
): 
    users: object = db.query(UserTable).all()         
    return users

@router.get("/{id}", response_model=UserResponseSchema)
def get_user_by_id(
    id: int, 
    user_payload = Depends(get_user_jwt_payload),
    db: Session = Depends(get_db)
):  
    # Fixed lookup field property path to check matching identity user_id attributes correctly
    fetched_user = db.query(UserTable).filter(UserTable.user_id == id).first()
    
    if not fetched_user:
        raise HTTPException(status_code=404, detail="User Not Found!")
    return fetched_user