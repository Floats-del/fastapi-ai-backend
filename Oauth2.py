from fastapi import Depends, status, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta  
from utils.schemas import TokenDataSchema
from fastapi.security import OAuth2PasswordBearer
from utils.config import settings

SECRET_KEY = settings.hash_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data: dict) -> str: #this dict is payload btw! which is user_id currently
    """Encodes operational dict data into signed JWT Access string."""
    to_encode_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode_data.update({"exp": expire})
    
    return jwt.encode(to_encode_data, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str, credentials_exception) -> TokenDataSchema:
    """Decodes string and extracts user identities, protecting endpoints from malicious signatures."""
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        user_id_from_payload = payload.get("user_id")
        
        if user_id_from_payload is None:
            raise credentials_exception
    
        token_data = TokenDataSchema(user_id=user_id_from_payload)
    except JWTError:
        raise credentials_exception
    
    return token_data

def get_user_jwt_payload(token: str = Depends(oauth2_scheme)) -> TokenDataSchema:
    """FastAPI Dependency enforcing explicit bearer authorization validation checks."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return verify_access_token(token=token, credentials_exception=credentials_exception)