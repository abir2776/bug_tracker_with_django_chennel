# Bug Tracker with Django Channels

A real-time bug tracking application built with Django and Django Channels, featuring WebSocket communication for live updates and a RESTful API for project and user management.

## Features

- **Real-time Communication**: WebSocket integration using Django Channels for live bug updates
- **User Authentication**: JWT-based authentication system
- **Project Management**: Create and manage bug tracking projects
- **RESTful API**: Comprehensive API endpoints for all operations
- **WebSocket Testing**: Built-in management command for testing WebSocket connectivity

## Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/abir2776/bug_tracker_with_django_chennel.git
cd bug_tracker_with_django_chennel
```

### 2. Create and Activate Virtual Environment

**For Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## API Documentation

### Authentication Endpoints

#### Register a New User
**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "your_password",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### Obtain JWT Token
**Endpoint:** `POST /api/token`

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "your_access_token",
    "refresh": "your_refresh_token"
}
```

### Project Management

#### Create a Project
**Endpoint:** `POST /api/projects`

**Headers:**
```
Authorization: Bearer your_access_token
Content-Type: application/json
```

**Request Body:**
```json
{
    "name": "My Bug Tracker Project",
    "description": "Project description here"
}
```

**Response:**
```json
{
    "id": 1,
    "name": "My Bug Tracker Project",
    "description": "Project description here",
    "created_at": "2025-01-01T12:00:00Z",
    "owner": 1
}
```

#### Get All Projects
**Endpoint:** `GET /api/projects`

**Headers:**
```
Authorization: Bearer your_access_token
```

#### Get Project Details
**Endpoint:** `GET /api/projects/{project_id}`

**Headers:**
```
Authorization: Bearer your_access_token
```

## WebSocket Integration

The application uses Django Channels for real-time communication. WebSocket connections are established for each project to enable live bug updates.

### WebSocket Endpoint
```
ws://127.0.0.1:8000/ws/project/{project_id}/
```

### Testing WebSocket Connectivity

#### 1. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
WEBSOCKET_TEST_USER_EMAIL="your_test_user@gmail.com"
WEBSOCKET_TEST_USER_PASS="your_password"
```

#### 2. Run WebSocket Test Command

Test WebSocket connectivity for a specific project:

```bash
python manage.py test_websocket <project_id>
```

**Example:**
```bash
python manage.py test_websocket 11
```

This command will:
- Authenticate the test user using credentials from `.env`
- Connect to the WebSocket endpoint for the specified project
- Send a test message and display responses in the console
- Verify the WebSocket connection is working properly

## Project Structure

```
bug_tracker_with_django_chennel/
├── manage.py
├── requirements.txt
├── .env (create this file)
├── README.md
├── bugtracker/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
└── common/
|__ tracker/
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# WebSocket Testing
WEBSOCKET_TEST_USER_EMAIL="test@example.com"
WEBSOCKET_TEST_USER_PASS="testpassword"
```
### 1. Complete User Registration and Project Creation Flow

```bash
# 1. Register a new user
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# 2. Get JWT token
curl -X POST http://127.0.0.1:8000/api/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# 3. Create a project (replace YOUR_TOKEN with actual token)
curl -X POST http://127.0.0.1:8000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Bug Tracker",
    "description": "Tracking bugs for our main website"
  }'
```
**Happy coding! 🚀**

For more information, visit the [project repository](https://github.com/abir2776/bug_tracker_with_django_chennel).