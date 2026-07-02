[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-success)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)

# FastAPI AI Backend Platform

A production-inspired backend platform built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and modern AI engineering practices.

Originally started as a social media backend, the project gradually evolved into a modular backend platform focused on building secure, observable, and scalable AI-powered services.

Rather than exposing AI models directly, the backend introduces standardized service contracts, centralized security, structured logging, AI gateways, response recovery, and clean layered architecture to provide a robust foundation for future AI applications.

---

# Table of Contents

- Overview
- Core Features
- Backend Architecture
- Request Lifecycle
- AI Platform
- AI Gateway
- Prompt Injection Protection
- AI Output Recovery
- Authentication
- Database
- Logging & Observability
- Error Handling
- Project Structure
- Tech Stack
- Development Status
- Roadmap
- Future Vision

---

# Overview

The backend is designed around one primary goal:

> **Every backend service should behave consistently regardless of whether it performs CRUD operations or AI processing.**

To achieve this, the project follows a standardized layered architecture.

Every request follows the same lifecycle:

```

Client
│
▼
FastAPI Route
│
▼
Gateway
│
▼
Service Layer
│
▼
Business Logic
│
▼
APIResponse
│
▼
Response Handler
│
▼
Global Exception Handler
│
▼
HTTP Response

```

Routes remain intentionally small while business logic lives entirely inside services.

---

# Core Features

## Backend

- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Async SQLAlchemy
- Alembic Migrations
- JWT Authentication
- OAuth2 Password Flow
- Password Hashing
- Pydantic Validation
- Layered Architecture
- Global Exception Handling
- Centralized API Responses
- Structured Logging

---

## Social Platform

Implemented Features

- User Registration
- Login
- JWT Authentication
- Protected Routes
- Create Posts
- Update Posts
- Delete Posts
- Search Posts
- Public / Private Posts
- Comments
- Likes
- User Relationships

Database Relationships

- User → Posts
- User → Comments
- User ↔ Posts (Likes)
- Post → Comments

---

# Backend Architecture

The project follows a clean layered architecture.

```

Route
│
▼
Gateway
│
▼
Service
│
▼
Business Logic
│
▼
APIResponse
│
▼
handle_service_response()
│
▼
AppException
│
▼
Global Exception Handler
│
▼
HTTP Response

```

Each layer has a single responsibility.

### Routes

Routes only:

- Receive requests
- Validate dependencies
- Call services
- Return responses

No business logic is placed inside routes.

---

### Services

Services contain:

- Validation
- Authorization
- Database operations
- AI execution
- Business rules
- Logging

Every service returns the same response object.

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
    error_code="...",
    error_message="..."
)
```

---

# Request Lifecycle

Every backend request follows a standardized flow.

```

Incoming Request
│
▼
Validation
│
▼
Authentication
│
▼
Authorization
│
▼
Gateway
│
▼
Business Logic
│
▼
Database / AI Provider
│
▼
APIResponse
│
▼
Response Handler
│
▼
HTTP Response

```

This keeps every backend endpoint predictable and easy to maintain.

---

# AI Platform

The project contains several modular AI services.

Implemented modules:

- Text Rephrasing
- Text Summarization
- Sentiment Analysis
- AI Title Generation
- Intent Classification

Each module follows the exact same execution pipeline.

```

Request
│
▼
Validation
│
▼
Intent Classification
│
▼
Security Checks
│
▼
Provider
│
▼
Structured Parsing
│
├──────────────┐
│              │
▼              ▼
Success     Recovery
│              │
└──────► APIResponse

```

Because every module follows the same architecture, adding new AI services requires minimal additional infrastructure.

---

# AI Gateway

All AI requests pass through a centralized gateway before reaching any language model.

Responsibilities include:

- Input validation
- Intent classification
- Security validation
- Prompt injection detection
- AI quota verification
- Request logging

This prevents duplicated security logic across AI services while keeping individual modules focused on their specific tasks.

---
# Prompt Injection Protection

Every AI request passes through multiple layers of security before reaching any LLM.

Security Pipeline

```
User Input
│
▼
Deterministic Rule-Based Detection
│
▼
Intent Classification
│
▼
Security Validation
│
▼
Accept / Reject
│
▼
AI Provider
```

The system differentiates between:

- Legitimate AI requests
- Educational security discussions
- Prompt injection attempts
- Jailbreak attempts
- Unknown inputs

Potentially malicious requests are rejected before reaching downstream providers.

---

# AI Output Recovery

LLMs occasionally produce malformed or partially structured outputs.

Instead of immediately failing, the backend attempts multiple recovery strategies before returning an error.

Recovery Pipeline

```
LLM Response
│
▼
Structured Parsing
│
├──────────────┐
│              │
▼              ▼
Success      Parsing Failed
│              │
▼              ▼
Return    Manual Recovery
│              │
├──────────────┐
│              │
▼              ▼
Recovered    Failed
│              │
▼              ▼
Return     APIResponse(Error)
```

This greatly improves robustness while maintaining a consistent response format.

---

# Authentication

Authentication is handled using JWT Bearer Tokens.

Implemented Features

- User Registration
- User Login
- Password Hashing (bcrypt)
- JWT Access Tokens
- OAuth2 Password Flow
- Protected Endpoints
- Token Validation

Every protected endpoint resolves the authenticated user before executing business logic.

Future authentication improvements include:

- Google OAuth
- OTP Verification
- JWT Revocation
- Refresh Token Improvements

---

# Authorization

Current authorization is user-based.

Planned authorization improvements include role-based access control.

Planned roles:

- User
- Pro User
- Administrator

Role-based authorization will be enforced through reusable dependencies to ensure consistent permission handling across all endpoints.

---

# AI Usage Management

To prevent abuse and support future subscription plans, AI requests are tracked per user.

Current implementation includes:

- Database-backed quota tracking
- Daily usage limits
- 24-hour cooldown period
- Row-level locking
- Concurrent request protection

The quota system is designed to remain safe even under concurrent requests.

---

# Logging & Observability

The backend uses centralized structured logging.

Instead of scattered logging statements, every service emits standardized lifecycle events.

Current logging categories include:

- Gateway Logs
- Service Logs
- Provider Logs
- Security Logs
- Repair Logs
- Authentication Logs
- User Logs
- Posting Logs

Typical service lifecycle:

```
SERVICE_STARTED
│
▼
VALIDATING_REQUEST
│
▼
EXECUTING_DATABASE_QUERY
│
▼
SUCCESS / OPERATION_FAILED
│
▼
EXITING_SERVICE
```

This makes debugging and monitoring significantly easier while keeping logging consistent across the codebase.

---

# Error Handling

The project uses a centralized exception framework.

```
Route
│
▼
Service
│
▼
APIResponse
│
▼
handle_service_response()
│
▼
AppException
│
▼
Global Exception Handler
│
▼
HTTP Response
```

Expected failures return:

```python
APIResponse(
    success=False,
    error_code="...",
    error_message="..."
)
```

Unexpected failures are converted into standardized responses through the global exception handler.

This approach keeps business logic independent from HTTP concerns.

---

# Database

Current schema:

```
users
│
├── posts
├── comments
├── likes
└── ai_usage_tracker
```

Relationships include:

- User → Posts
- User → Comments
- User ↔ Posts (Likes)
- Post → Comments

Database migrations are managed using Alembic.

---

# Project Structure

```
.
├── Ai/
│   ├── gateway.py
│   ├── intent_classifier.py
│   ├── rephraser.py
│   ├── summary.py
│   ├── sentiment_analysis.py
│   ├── title_generator.py
│   ├── raw_and_parsed_clean.py
│   ├── retry_logic.py
│   └── ...
│
├── routers/
│   ├── ai.py
│   ├── auth.py
│   ├── users.py
│   ├── posts.py
│   └── ...
│
├── services/
│
├── db_tables/
│
├── core/
│   ├── exceptions.py
│   ├── handlers.py
│   └── responses.py
│
├── logging/
│
├── utils/
│
├── alembic/
│
├── tests/
│
└── main.py
```

The project is continuously being refactored toward a cleaner layered architecture with standardized service contracts.

---

# Tech Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- Async SQLAlchemy
- PostgreSQL
- Alembic

## Authentication

- JWT
- OAuth2 Password Flow
- Passlib (bcrypt)

## AI

- LangChain
- LLM Providers
- Structured Output Parsing
- Prompt Injection Detection
- Intent Classification
- Automatic Output Recovery

## Development

- Pydantic
- AsyncIO
- Structured Logging
- Custom Exception Framework

# Current Development Status

## Completed

### Core Backend

- FastAPI REST API
- PostgreSQL Integration
- Async SQLAlchemy Migration
- Alembic Database Migrations
- Layered Backend Architecture
- Service Layer Refactoring
- Centralized API Response Contract
- Global Exception Framework
- Structured Logging Framework

---

### Authentication

- User Registration
- User Login
- JWT Authentication
- OAuth2 Password Flow
- Password Hashing
- Protected Routes

---

### Social Platform

- Create Posts
- Update Posts
- Delete Posts
- Search Posts
- Public / Private Posts
- Comments
- Likes
- User Relationships

---

### AI Platform

- AI Gateway
- Intent Classification
- Prompt Injection Detection
- Text Rephrasing
- Text Summarization
- Sentiment Analysis
- AI Title Generation
- Structured Output Parsing
- Automatic Output Recovery
- Provider Retry Logic
- AI Usage Quota Tracking

---

### Backend Engineering

- APIResponse Standardization
- Layered Service Architecture
- Async Database Operations
- Race Condition Protection
- Row-Level Database Locking
- Centralized Logging
- Custom Exception Hierarchy
- Standardized Service Lifecycle

---

# Currently In Development

The project is actively evolving toward a production-ready AI backend platform.

Current priorities include:

- AI moderation for user-generated posts and comments
- Gateway standardization across all backend routes
- OTP-based authentication
- Google OAuth integration
- Subscription and role-based authorization
- LangSmith observability integration
- AI abuse detection and temporary bans
- Continued backend cleanup and architectural refinement

---

# Roadmap

## Authentication

- OTP Verification
- Google OAuth
- Refresh Token Improvements
- JWT Revocation
- Multi-device Session Management

---

## Authorization

- Role-Based Access Control
- Subscription Plans
- Premium AI Features
- Administrative Dashboard

---

## AI Platform

- Multi-Provider Support
- Provider Failover
- Provider Load Balancing
- RAG Integration
- AI Agents
- Conversation Memory
- AI Workflow Orchestration

---

## Observability

- LangSmith Tracing
- Metrics Dashboard
- Request Analytics
- AI Performance Monitoring
- Centralized Health Checks

---

## Scalability

- Redis Caching
- Distributed Rate Limiting
- Token Bucket Algorithm
- Route Locking
- Background Task Queue
- Worker-Based AI Processing
- Horizontal Scaling Support

---

## DevOps

- Docker
- Docker Compose
- CI/CD Pipeline
- Production Deployment
- Kubernetes
- Environment-Based Configuration

---

# Engineering Principles

This project follows a set of engineering principles that guide every feature and refactor.

- Thin API Routes
- Business Logic Inside Services
- Consistent APIResponse Contract
- Centralized Exception Handling
- Standardized Logging
- Modular AI Components
- Security Before AI Execution
- Async-First Database Operations
- Reusable Infrastructure
- Production-Oriented Design

Rather than solving problems individually, new features are built on reusable infrastructure so they naturally integrate with the rest of the platform.

---

# Future Vision

The long-term goal of this project is to become a modular backend platform capable of supporting AI-powered applications through standardized infrastructure.

Rather than being tied to a single AI feature or provider, the platform is designed so that new capabilities can be introduced with minimal architectural changes.

Areas of future exploration include:

- Enterprise Authentication
- AI Workflow Automation
- Retrieval-Augmented Generation (RAG)
- AI Agents
- Multi-Model Routing
- Streaming AI Responses
- Distributed AI Services
- Cloud-Native Deployment

---

# Learning Goals

This repository serves as a practical exploration of modern backend engineering concepts, including:

- Backend Architecture
- Software Design Patterns
- Secure API Development
- Authentication & Authorization
- AI Integration
- Observability
- Database Engineering
- Concurrency Handling
- Scalable Backend Design
- Production Engineering Practices

The project is intentionally built from the ground up without relying on backend templates, allowing each architectural decision to be understood, implemented, and refined throughout development.

---

# Contributing

This project is currently a personal learning and engineering project.

Suggestions, discussions, issue reports, and constructive feedback are always welcome.

---

# License

This project is licensed under the MIT License.

---

# Author

**Floats**

Backend Developer • AI Enthusiast • Software Engineering Student

This project documents my journey of learning backend engineering, AI integration, and production-inspired software architecture by building and continuously refining a real-world FastAPI platform from the ground up.

