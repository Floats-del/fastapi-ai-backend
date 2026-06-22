# FastAPI AI Social Backend

A production-oriented backend API built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and AI-powered services.

This project started as a social network backend and evolved into an AI-integrated platform with standardized AI service handling, authentication, database migrations, and scalable backend patterns.

---

# Features

## Core Backend

- FastAPI REST API
- PostgreSQL database
- SQLAlchemy ORM
- Alembic database migrations
- JWT authentication
- Password hashing using bcrypt
- CORS configuration
- Pydantic validation schemas

---

# Social Features

Implemented:

- User registration
- User authentication
- JWT protected routes
- Create posts
- Update posts
- Delete posts
- Search posts
- Public/private posts
- Likes system
- Comments system

Database relationships:

- User → Posts (One-to-Many)
- User ↔ Posts (Many-to-Many through Likes)
- User → Comments
- Post → Comments

---

# AI Integration

The project contains multiple AI-powered services:

Implemented AI services:

- Text Rephrasing
- Text Summarization
- Sentiment Analysis
- AI Title Generation


## AI Service Architecture

All AI services follow a standardized pipeline:

```
Request
   |
   v
AI Service
   |
   v
Model Processing
   |
   v
APIResponse
   |
   +----------------+
   |                |
 Success         Failure
   |                |
Return Data     Error Handling
```

---

# AI Response Standardization

All AI modules return:

```python
APIResponse(
    success=True/False,
    data=result,
    error_code=None,
    error_message=None
)
```

This creates a consistent contract between:

- AI services
- API routes
- Error handlers

---

# Error Handling Architecture

Custom exception hierarchy:

```
Exception
   |
AppException
   |
AIServiceException
```

Global exception handling converts application failures into standardized API responses.

Handled cases:

- AI failures
- Unknown system errors
- Invalid AI responses

---

# AI Quota System

Implemented user-level AI usage control.

Features:

- Database tracked usage
- 24 hour cooldown system
- Row locking for concurrent requests
- Prevents quota bypass through race conditions

Database table:

```
ai_usage_tracker
```

---

# Database

Current tables:

```
users
 |
 +-- posts
 |
 +-- comments
 |
 +-- likes


ai_usage_tracker
```

Database migrations managed through:

```
Alembic
```

---

# Tech Stack

Backend:

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic

Authentication:

- JWT
- OAuth2 Password Flow
- Passlib bcrypt

AI:

- LLM based processing
- Structured AI responses
- AI service abstraction

---

# Project Structure

```
.
├── Ai/
│   ├── main.py
│   ├── title_gen.py
│   ├── summry_ai.py
│   ├── sentiment_analysis_ai.py
│   └── Ai_rephrase_content.py
│
├── routers/
│   ├── ai.py
│   ├── posts.py
│   ├── users.py
│   ├── likes.py
│   └── auth.py
│
├── db_tables/
│   └── tables.py
│
├── core/
│   ├── exceptions.py
│   └── exception_handlers.py
│
├── utils/
│   ├── schemas.py
│   ├── config.py
│   └── hashing.py
│
├── alembic/
│
├── db.py
├── Oauth2.py
└── code1.py
```

---

# Current Development Status

✅ Database architecture completed  
✅ Authentication completed  
✅ Social features completed  
✅ AI services standardized  
✅ Custom exception system added  
✅ AI quota management implemented  

Currently working on:

- Standardizing remaining routes
- Moving older routes to the new error handling pattern
- Further AI pipeline improvements

---

# Future Improvements

Planned:

- Fully async route migration
- API gateway pattern
- More AI modules
- RAG integration
- AI agents
- Better observability/logging
- Production deployment

---

# Author

Backend AI engineering learning project.