from datetime import datetime, timezone

from db import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class PostTable(Base): 
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")) 
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE", onupdate="SET DEFAULT"), nullable=False)
    
    owner = relationship("UserTable", back_populates="posts")
    likers = relationship("UserTable", secondary="likes", back_populates="liked_posts")
    comments = relationship("CommentTable", back_populates="post", cascade="all, delete-orphan")


class UserTable(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")) 
    
    posts = relationship("PostTable", back_populates="owner")
    liked_posts = relationship("PostTable", secondary="likes", back_populates="likers")
    comments = relationship("CommentTable", back_populates="commenter", cascade="all, delete-orphan")


class LikeTable(Base):
    __tablename__ = "likes"
    
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), primary_key=True)


class CommentTable(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    text = Column(String, nullable=False)
    
    # FIX: Changed from text("now()") to func.now() to prevent variable name collision
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)

    post = relationship("PostTable", back_populates="comments")
    commenter = relationship("UserTable", back_populates="comments")
    """
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE", onupdate="SET_DEFAULT"), nullable=False)
    #the dtype should match the dtype of foregin key, the ForeigenKey's 1st arg is related table's name .id which is what we 
        #wanted realtion on!
    
    # 2. SQLAlchemy relationship: Links this post to its owner object
    owner = relationship(
        "user_table", #class name 
        back_populates="posts" #link with posts var in above class name
        
    ) #Column(Integer, ForeignKey ... is not enough! coz this talks to the db and relationship() tells this to python!
        #coz in ForeignKey ORM only sees an integer... not much value so we need relationships to tell orm the realtion
            #vr trying to make via foreginkey
    """



class AIUsageTrackerTable(Base):
    __tablename__ = "ai_usage_tracker"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    last_used = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )