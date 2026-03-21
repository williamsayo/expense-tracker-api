# Expense Tracker API

A modern, production-ready expense tracking application built with **Domain-Driven Design (DDD)** principles. This project demonstrates clean architecture patterns, async-first development with FastAPI, and comprehensive domain modeling for financial transaction management.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Development Workflow](#development-workflow)
- [Project Domains](#project-domains)
- [Contributing](#contributing)

## 🎯 Overview

The Expense Tracker API is a FastAPI-based backend service that manages:

- **User Identity**: Authentication and user profile management
- **Expenses**: Recording and tracking individual financial transactions
- **Budgets**: Setting and monitoring budget allocations across categories

Built with **Domain-Driven Design**, each domain is completely autonomous with its own:

- Business logic (domain layer)
- Use cases and workflows (application layer)
- Data persistence (infrastructure layer)
- HTTP endpoints (presentation layer)

## 🏗️ Architecture

### Domain-Driven Design (DDD)

This project strictly follows DDD principles:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (FastAPI Routes, DTOs, Request/Response)
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│       Application Layer                 │
│ (Use Cases, Services, Port Definitions) │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│       Domain Layer                      │
│ (Entities, Value Objects, Aggregates,  │
│  Domain Rules, Business Logic)          │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│      Infrastructure Layer               │
│ (Repositories, Adapters, Database,     │
│  External Service Integrations)         │
└─────────────────────────────────────────┘
```

### Key DDD Concepts

- **Aggregates**: Clusters of entities treated as a single unit (e.g., `BudgetEntity` with related `BudgetAllocationEntity`)
- **Value Objects**: Immutable objects that represent concepts (e.g., `MoneyValueObject`, `CategoryValueObject`)
- **Repositories**: Abstract data persistence, allowing domain entities to be stored and retrieved
- **Domain Events**: Events that capture significant business occurrences
- **Bounded Contexts**: Each domain (Identity, Expenses, Budgeting) is a separate bounded context

## 📁 Project Structure

```
expense-tracker-ddd/
├── src/
│   ├── main.py                          # FastAPI application entry point
│   │
│   ├── identity/                        # User Authentication Domain
│   │   ├── domain/                      # Core business logic
│   │   │   ├── entities/                # User entity definitions
│   │   │   └── value_objects/           # Email, password, etc.
│   │   ├── application/                 # Use cases and services
│   │   │   ├── dto/                     # Data transfer objects
│   │   │   └── services/                # Business operations
│   │   ├── infrastructure/              # Data persistence
│   │   │   ├── repositories/            # User repository implementation
│   │   │   ├── mappers/                 # Domain ↔ ORM mapping
│   │   │   └── services/                # External integrations
│   │   └── presentation/                # HTTP API
│   │       └── web/v1/route.py          # Authentication endpoints
│   │
│   ├── expenses/                        # Expense Tracking Domain
│   │   ├── domain/
│   │   │   ├── entities/                # Expense entity
│   │   │   └── value_objects/           # Amount, category, etc.
│   │   ├── application/
│   │   │   ├── dto/                     # Expense DTOs
│   │   │   └── services/                # Expense use cases
│   │   ├── infrastructure/
│   │   │   ├── repositories/            # Expense persistence
│   │   │   └── mappers/                 # Expense mapping logic
│   │   └── presentation/
│   │       └── web/v1/route.py          # Expense endpoints
│   │
│   ├── budgeting/                       # Budget Management Domain
│   │   ├── domain/
│   │   │   ├── entities/                # Budget and allocation entities
│   │   │   └── value_objects/           # Period, allocation rules, etc.
│   │   ├── application/
│   │   │   ├── dto/                     # Budget DTOs
│   │   │   └── services/                # Budget use cases
│   │   ├── infrastructure/
│   │   │   ├── repositories/            # Budget persistence
│   │   │   ├── mappers/                 # Budget mapping logic
│   │   │   └── schema.py                # SQLAlchemy ORM models
│   │   └── presentation/
│   │       └── web/v1/route.py          # Budget endpoints
│   │
│   ├── shared/                          # Cross-domain utilities
│   │   ├── domain/                      # Shared value objects and types
│   │   ├── infrastructure/
│   │   │   └── db/                      # Database configuration
│   │   ├── loggers/                     # Logging setup
│   │   └── errors/                      # Shared error definitions
│   │
│   └── core/                            # Application configuration
│       ├── config.py                    # Settings from environment
│       ├── exception_handler.py         # Global error handling
│       └── middlewares.py               # CORS, logging, etc.
│
├── tests/                               # Test suite (unit, integration)
├── pyproject.toml                       # Project dependencies and config
├── .env.local                           # Local environment variables
└── README.md                            # This file
```

## 🛠️ Technology Stack

| Layer              | Technology                            | Purpose                           |
| ------------------ | ------------------------------------- | --------------------------------- |
| **Framework**      | FastAPI 0.135.1+                      | Modern async web framework        |
| **Python**         | 3.13+                                 | Language runtime                  |
| **Database**       | SQLAlchemy 2.0.48+                    | ORM and database toolkit          |
| **SQLite**         | aiosqlite                             | Async SQLite driver               |
| **Authentication** | PyJWT 2.12.1                          | JWT token generation/validation   |
| **Hashing**        | Argon2 CFI                            | Password hashing                  |
| **Validation**     | Pydantic 2.12.5+                      | Data validation and serialization |
| **DDD Tooling**    | domain-driven-design-boilerplate-core | Reusable DDD base classes         |
| **Error Handling** | result-boilerplate                    | Railway-oriented result types     |
| **Code Quality**   | Ruff                                  | Linting and formatting            |

## 📦 Prerequisites

Before running this project, ensure you have:

- **Python 3.13+** installed
- **pip** or **uv** package manager
- **Git** for version control
- A terminal/command prompt

Verify your Python version:

```bash
python --version
# Expected: Python 3.13.0 or higher
```

## 🚀 Installation

### 1. Clone the Repository

```bash
cd backend_api
```

### 2. Create a Virtual Environment

**Using venv:**

```bash
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on macOS/Linux:
source .venv/bin/activate
```

**Using uv (faster):**

```bash
uv venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
# Using pip
pip install -e .

# Or using uv
uv sync
```

This installs:

- FastAPI and Uvicorn (web server)
- SQLAlchemy (ORM)
- Pydantic (validation)
- JWT and password hashing libraries
- DDD boilerplate utilities

## ⚙️ Environment Setup

### Create Environment File

Create a `.env.local` file in the project root:

```bash
# Database Configuration
DB_URL=sqlite+aiosqlite:///./local.db
DB_NAME=expense_tracker
DB_USER=default
DB_PASSWORD=password

# Redis Configuration (optional, for caching)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Settings
APP_NAME=Expense Tracker API
ENVIRONMENT=development
VERSION=0.1.0
DEBUG=true

# Security (JWT)
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Password Hashing (Argon2)
MEMORY_COST=65536
TIME_COST=3
PARALLELISM=4
HASH_LEN=32
SALT_LEN=16

# Logging
BETTER_STACK_API_TOKEN=your_api_token
```

### Environment Variable Guide

| Variable      | Required | Example                          | Description                                 |
| ------------- | -------- | -------------------------------- | ------------------------------------------- |
| `DB_URL`      | ✅       | `sqlite+aiosqlite:///./local.db` | Database connection string                  |
| `SECRET_KEY`  | ✅       | `your-secret-key`                | JWT signing key (min 32 chars in prod)      |
| `ENVIRONMENT` | ❌       | `development`                    | `development` or `production`               |
| `DEBUG`       | ❌       | `true`                           | Enable debug mode (set false in production) |
| `REDIS_URL`   | ❌       | `redis://localhost:6379/0`       | Redis connection for caching                |

## ▶️ Running the Application

### Start the Development Server

```bash
cd src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This will:

- Start Uvicorn on `http://localhost:8000`
- Enable auto-reload on file changes (great for development)
- Initialize the SQLite database if it doesn't exist

**Output:**

```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Access Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Documentation

### Authentication Domain (`/api/v1/auth`)

#### Register User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": { ... }
}
```

### Expenses Domain (`/api/v1/expenses`)

#### Create Expense

```http
POST /api/v1/expenses
Authorization: Bearer {token}
Content-Type: application/json

{
  "amount": 45.50,
  "currency": "EUR",
  "category": "FOOD",
  "date": "2025-03-21",
  "note": "Grocery shopping"
}
```

#### List User Expenses

```http
GET /api/v1/expenses
Authorization: Bearer {token}
```

### Budgets Domain (`/api/v1/budgets`)

#### Create Budget

```http
POST /api/v1/budgets
Authorization: Bearer {token}
Content-Type: application/json

{
  "start_date": "2025-03-01",
  "end_date": "2025-03-31",
  "allocations": [
    {
      "category": "FOOD",
      "amount": 500,
      "currency": "EUR"
    }
  ]
}
```

#### List Budgets

```http
GET /api/v1/budgets
Authorization: Bearer {token}
```

See the interactive API docs at `/docs` for complete endpoint specifications.

## 🔄 Development Workflow

### Code Organization Best Practices

#### 1. **Adding a New Use Case**

Create files in the application layer:

```
expenses/application/
├── services/
│   └── expense_service.py      # Add new use case method
├── dto/
│   └── expense.py              # Add request/response DTO
```

#### 2. **Creating Domain Logic**

Define business rules in the domain layer:

```python
# expenses/domain/entities/expense_entity.py
class ExpenseEntity(AggregateRoot):
    def validate_amount(self) -> Either[None, DomainRuleError]:
        """Business rule: expense amount must be positive"""
        if self.money.amount <= 0:
            return result_fail(DomainRuleError(...))
        return result_ok()
```

#### 3. **Mapping Between Layers**

Use mappers to convert between domain and persistence:

```python
# expenses/infrastructure/mappers/expense_mapper.py
class ExpenseMapper(BaseMapper):
    @staticmethod
    def to_persistence(entity: ExpenseEntity) -> Expense:
        """Convert domain entity to ORM model"""
        ...

    @staticmethod
    def to_domain(persistence: Expense) -> Either[ExpenseEntity, CoreError]:
        """Convert ORM model to domain entity"""
        ...
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/expenses/test_expense_entity.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code with Ruff
ruff format src/

# Lint with Ruff
ruff check src/ --fix

# Type checking (if configured)
mypy src/
```

## 📦 Project Domains

### 1. **Identity Domain**

Manages user authentication and profiles.

**Key Entities:**

- `UserEntity` - User account information
- `EmailValueObject` - Validated email address

**Key Use Cases:**

- User registration
- User login authentication
- User profile retrieval

---

### 2. **Expenses Domain**

Tracks individual financial transactions.

**Key Entities:**

- `ExpenseEntity` - Single expense transaction
- `MoneyValueObject` - Amount and currency
- `CategoryValueObject` - Expense category

**Key Use Cases:**

- Create expense
- List user expenses
- Update expense
- Delete expense
- Filter by category/date

---

### 3. **Budgeting Domain**

Allocates and monitors budgets across categories.

**Key Entities:**

- `BudgetEntity` - aggregate root for budget
- `BudgetAllocationEntity` - Category-specific allocation
- `BudgetPeriodValueObject` - Start/end dates

**Key Use Cases:**

- Create budget with allocations
- List budgets by user
- Update budget period
- Manage allocations
- Track spending vs. budget

---

### 4. **Shared Utilities**

Cross-domain infrastructure and types.

**Includes:**

- Database configuration and migrations
- Shared DTOs and error types
- Logging setup
- JWT utilities

## 🆘 Troubleshooting

### Database Issues

**Error: SQLAlchemy MissingGreenlet**

- Ensure async relationships are eager-loaded using `selectinload()`
- Check that lazy-loading doesn't occur in async contexts

**Error: Database locked**

- SQLite has concurrency limitations; consider PostgreSQL for production

### Authentication Issues

**Invalid token error**

- Verify `SECRET_KEY` is set and consistent
- Check token expiration time
- Ensure `Authorization: Bearer {token}` header format

### Environment Issues

**ModuleNotFoundError**

- Activate the virtual environment
- Reinstall dependencies: `pip install -e .`
- Check Python version is 3.13+

---

**Last Updated**: March 2026  
**Maintainer**: Your Name
