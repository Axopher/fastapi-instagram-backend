# FastAPI Social App Backend

A backend built with FastAPI and SQLAlchemy.

## 🚀 Features

- User registration, following/unfollowing
- Alembic for database migrations
- Token-based auth

## 🛠️ Setup

1. Clone the repo and get inside the project directory
2. Install dependencies:

```
pipenv install --dev
pipenv shell
```

3. Set up environment:

```
cp .env.example .env
```

# Edit the .env file with actual secrets and DB credentials

4. Run migrations

```
alembic upgrade head
```

5. start the app:

```
uvicorn src.main:app --reload
```
