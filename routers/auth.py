from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from utils.schemas import TokenSchema
from db_tables.tables import UserTable
from utils.hashing import verify_hashed_password
from Oauth2 import create_access_token
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])

@router.post('/login', response_model=TokenSchema)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    fetched_user = db.query(UserTable).filter(UserTable.email == user_credentials.username).first()

    if not fetched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!")
    
    if not verify_hashed_password(user_credentials.password, fetched_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    access_token = create_access_token(data={"user_id": fetched_user.user_id}) 
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }