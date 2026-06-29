[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# FastAPI AI Backend Platform

A production-oriented backend built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and modular AI services.

Originally developed as a social media backend, the project has evolved into an AI-powered backend platform focused on standardized AI service architecture, security, observability, and scalable backend engineering practices.

---

# Features

## Core Backend

- FastAPI REST API
- PostgreSQL
- SQLAlchemy ORM
- Alembic Database Migrations
- JWT Authentication
- OAuth2 Password Flow
- Password Hashing (bcrypt)
- Pydantic Validation
- CORS Configuration

---

# Social Features

Implemented:

- User Registration
- User Authentication
- JWT Protected Routes
- Create Posts
- Update Posts
- Delete Posts
- Search Posts
- Public / Private Posts
- Likes System
- Comments System

Database Relationships:

- User → Posts (One-to-Many)
- User ↔ Posts (Many-to-Many through Likes)
- User → Comments
- Post → Comments

---

# AI Services

Implemented AI modules:

- Text Rephrasing
- Text Summarization
- Sentiment Analysis
- AI Title Generation
- AI Intent Classification

---

# AI Pipeline Architecture

Every AI service follows the same standardized lifecycle.

```

Request
│
▼
Input Validation
│
▼
Intent Classification
│
▼
Deterministic Security Checks
│
▼
LLM Provider
│
▼
Structured Output Parsing
│
├───────────────┐
│               │
▼               ▼
Success      Manual Recovery
│               │
▼               ▼
APIResponse  APIResponse

```

This architecture allows every AI module to behave consistently while remaining resilient to malformed model outputs.

---

# Intent Classification

The AI gateway classifies incoming requests into semantic categories before processing.

Supported intents:

- Rephrase
- Title Generation
- Sentiment Analysis
- Summarization
- Casual Conversation
- Security Discussion
- Malicious Prompt Injection
- Unknown Input

---

# Prompt Injection Protection

The backend performs layered security checks before AI processing.

Security pipeline:

```

User Input
│
▼
Deterministic Regex Detection
│
▼
LLM Intent Classification
│
▼
Security Validation
│
▼
Accept / Reject

```

Malicious prompt injection attempts are blocked before reaching downstream AI services.

---

# AI Response Standardization

Every AI service returns the same response contract.

```python
APIResponse(
    success=True,
    data=result,
    error_code=None,
    error_message=None
)
```

or

```python
APIResponse(
    success=False,
    data=None,
    error_code=...,
    error_message=...
)
```

This creates a consistent interface between:

- AI Services
- API Routes
- Exception Handlers
- Frontend Clients

---

# AI Output Recovery

AI responses are processed using multiple validation stages.

```

LLM Output
│
▼
Structured Parsing
│
├─────────────┐
│             │
▼             ▼
Valid      Parsing Failed
│             │
▼             ▼
Return   Manual Recovery
│             │
└──────► APIResponse

```

This significantly improves robustness when models return imperfect structured outputs.

---

# Logging Architecture

The backend uses standardized structured logging.

Logging categories include:

- Gateway Logs
- Service Logs
- Provider Logs
- Repair Logs
- Security Logs
- Authentication Logs
- Reservation Logs

Every AI service logs:

- Service lifecycle
- Provider requests
- Provider failures
- Recovery attempts
- Security events
- Exceptions

This provides consistent observability across the entire backend.

---

# Error Handling Architecture

Custom exception hierarchy:

```

Exception
│
AppException
│
AIServiceException

```

Global exception handlers convert unexpected failures into standardized API responses.

Handled cases include:

- AI Provider Failures
- Invalid Structured Outputs
- Recovery Failures
- Authentication Errors
- Unknown System Exceptions

---

# AI Quota Management

Implemented user-level AI usage control.

Features:

- Database-backed quota tracking
- 24-hour cooldown system
- Row-level locking
- Race condition protection
- Concurrent request safety

Database table:

```

ai_usage_tracker

```

---

# Database

Current schema:

```

users
│
├── posts
├── comments
└── likes

ai_usage_tracker

```

Database migrations are managed using Alembic.

---

# Tech Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic

## Authentication

- JWT
- OAuth2 Password Flow
- Passlib (bcrypt)

## AI

- LLM-based Processing
- LangChain
- Structured Output Parsing
- Intent Classification
- Prompt Injection Detection
- Automatic Output Recovery

---

# Project Structure

```

.
├── Ai/
│   ├── intent_classifier.py
│   ├── rephraser.py
│   ├── summary.py
│   ├── sentiment_analysis.py
│   ├── title_generator.py
│   ├── raw_and_parsed_clean.py
│   └── retry_logic.py
│
├── routers/
│   ├── ai.py
│   ├── auth.py
│   ├── users.py
│   ├── posts.py
│   └── likes.py
│
├── core/
│   ├── exceptions.py
│   └── exception_handlers.py
│
├── db_tables/
│   └── tables.py
│
├── utils/
│   ├── logging/
│   ├── schemas.py
│   ├── hashing.py
│   └── config.py
│
├── alembic/
├── actual_test/
├── code1.py
├── db.py
└── Oauth2.py

```

---

# Current Development Status

Completed:

- ✅ FastAPI Backend
- ✅ Authentication
- ✅ Social Features
- ✅ AI Service Architecture
- ✅ Intent Classification
- ✅ Prompt Injection Detection
- ✅ AI Response Standardization
- ✅ Structured Logging
- ✅ Custom Exception Framework
- ✅ AI Output Recovery
- ✅ AI Quota Management

Currently Working On:

- Standardizing remaining AI services
- Shared AI infrastructure refactoring
- Route cleanup
- Improved observability
- Production readiness

---

# Planned Improvements

- Docker Support
- CI/CD Pipeline
- Multiple AI Provider Support
- Provider Failover
- RAG Integration
- AI Agent Framework
- Metrics Dashboard
- Distributed Tracing
- Production Deployment
- Kubernetes Support

---

# Author

**Floats** *(Real name coming soon 😉)*