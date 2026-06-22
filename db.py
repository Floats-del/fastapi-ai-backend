
#no async
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.config import settings

# Construct PostgreSQL connection URL using production settings
DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
) 

# Configure engine with robust connection pooling policies
engine = create_engine(
    DATABASE_URL, #for postgres, but if u put, 'sqlite:///mydb.db' here then in same dir ull have db ;)
    pool_size=20, 
    max_overflow=10, 
    pool_timeout=30, 
    pool_recycle=3600
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine) 
Base = declarative_base()

def get_db():
    db = SessionLocal()
        #get a session to db -> a portal to db
    try:
        yield db #return db to whoever called it 
    finally:
        db.close() #once said caller used db, we close  the session
"""


#async:
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from utils.config import settings


DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)


engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False
)


Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session #does the same process as in no async get_db() function