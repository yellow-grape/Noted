# Noted App

A modern web application with Django Ninja API backend and separate frontend.

## Project Structure
```
noted/
├── backend/         # Django Ninja API
│   ├── core/       # Main Django project
│   ├── apps/       # Django applications
│   └── api/        # API endpoints and schemas
└── frontend/       # Frontend application
```

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Features

- JWT Authentication
- User Profiles
- Image Upload and Management
- CORS configured
- API Documentation (available at /api/docs)

## API Endpoints

- `/api/auth/` - Authentication endpoints
- `/api/profiles/` - User profile management
- `/api/images/` - Image upload and management

## Technology Stack

### Backend
- Django
- Django Ninja
- Poetry for dependency management
- JWT Authentication
- PostgreSQL (recommended for production)

### Development Tools
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
