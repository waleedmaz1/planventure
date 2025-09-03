# Planventure API 🚁

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Flask Version](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-3.1.1-orange.svg)](https://www.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/jwt-enabled-yellow.svg)](https://jwt.io/)

A Flask-based REST API backend for the Planventure application - your comprehensive travel planning companion.

## 🌟 Features

- **🔐 Authentication System**: JWT-based authentication with refresh tokens
- **🏖️ Trip Management**: Complete CRUD operations for travel planning
- **🗺️ Itinerary Generation**: AI-powered automatic itinerary creation
- **📍 Location Support**: GPS coordinates and destination type detection
- **💰 Budget Tracking**: Trip budget management and tracking
- **🔒 Security**: Account lockout protection and password validation
- **🌐 CORS Ready**: Configured for React frontend integration
- **📊 Trip Statistics**: Comprehensive trip analytics

## 📁 Project Structure

```
planventure-api/
├── app.py                      # Main Flask application
├── create_db.py               # Database initialization script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── models/
│   ├── __init__.py
│   ├── base.py               # Base model with common fields
│   ├── user.py               # User model with authentication
│   └── trip.py               # Trip model with itinerary support
├── routes/
│   ├── __init__.py
│   ├── auth.py               # Authentication endpoints
│   └── trips.py              # Trip management endpoints
├── utils/
│   ├── __init__.py
│   ├── jwt_auth.py           # JWT token management
│   ├── middleware.py         # Authentication middleware
│   ├── validation.py         # Input validation utilities
│   ├── password.py           # Password hashing utilities
│   ├── itinerary.py          # Itinerary template generation
│   └── cors_config.py        # CORS configuration
└── test_examples/
    └── trips_test_examples.json
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/planventure.git
   cd planventure/planventure-api
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .sample.env .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python create_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a [`.env`](planventure-api/.env) file with the following variables:

```bash
# Database
DATABASE_URL=sqlite:///planventure.db

# Security
SECRET_KEY=your-secret-key-change-in-production

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=900
JWT_REFRESH_TOKEN_EXPIRES=2592000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
FLASK_ENV=development
FLASK_DEBUG=true
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication

All authenticated endpoints require an `Authorization` header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Endpoints Overview

#### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | User registration | ❌ |
| POST | `/login` | User login | ❌ |
| POST | `/refresh` | Refresh access token | ❌ |
| POST | `/validate-email` | Email validation | ❌ |
| GET | `/me` | Get current user info | ✅ |
| PUT | `/profile` | Update user profile | ✅ |

#### Trips (`/api/trips`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get all user trips | ✅ |
| POST | `/` | Create new trip | ✅ |
| GET | `/{id}` | Get specific trip | ✅ |
| PUT | `/{id}` | Update trip | ✅ |
| DELETE | `/{id}` | Delete trip | ✅ |
| GET | `/stats` | Get trip statistics | ✅ |
| GET | `/{id}/itinerary` | Get trip itinerary | ✅ |
| POST | `/{id}/itinerary/generate` | Generate itinerary | ✅ |
| GET | `/itinerary/templates` | Get itinerary templates | ✅ |

### Example Requests

#### User Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### Create Trip with Auto-Generated Itinerary
```bash
curl -X POST http://localhost:5000/api/trips \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "destination": "Bali, Indonesia",
    "start_date": "2024-08-01",
    "end_date": "2024-08-07",
    "latitude": -8.3405,
    "longitude": 115.0920,
    "description": "Beach vacation",
    "budget": 2000.00,
    "generate_itinerary": true,
    "destination_type": "beach"
  }'
```

#### Get Trips with Filtering
```bash
curl -X GET "http://localhost:5000/api/trips?status=planned&page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏖️ Itinerary System

The API features an intelligent itinerary generation system with support for multiple destination types:

### Destination Types
- **🏙️ City**: Museums, landmarks, cultural sites
- **🏖️ Beach**: Water sports, coastal activities, relaxation
- **⛰️ Mountain**: Hiking, adventure sports, nature activities
- **🏛️ Cultural**: Historical sites, temples, traditional experiences

### Auto-Detection
The system automatically detects destination types based on keywords in the destination name:
- "Bali Beach Resort" → Beach
- "Swiss Alps" → Mountain
- "Historic Temple Complex" → Cultural
- Default → City

### Trip Styles
- **Relaxed**: 2 activities/day, slow pace
- **Balanced**: 3 activities/day, moderate pace
- **Adventurous**: 4 activities/day, fast pace
- **Cultural**: 3 activities/day, culture-focused

## 🔒 Security Features

### Authentication
- JWT-based authentication with access and refresh tokens
- Secure password hashing using Werkzeug
- Account lockout protection after failed login attempts

### Validation
- Email format and availability validation
- Password strength requirements
- Input sanitization and validation
- Request rate limiting support

### CORS Configuration
- Configurable CORS origins for frontend integration
- Credential support for authenticated requests
- Secure headers configuration

## 🛠️ Development Tools

### Database Management
```bash
# Create all tables
python create_db.py

# Drop all tables
python create_db.py drop

# Reset database (drop and recreate)
python create_db.py reset
```

### Testing
Use the provided test examples in [`test_examples/trips_test_examples.json`](planventure-api/test_examples/trips_test_examples.json) for comprehensive API testing with tools like:
- [Bruno](https://usebruno.com/)
- Postman
- cURL

## 📦 Dependencies

### Core Dependencies
- **Flask 2.3.3**: Web framework
- **Flask-SQLAlchemy 3.1.1**: Database ORM
- **Flask-CORS 4.0.0**: Cross-origin resource sharing
- **Flask-JWT-Extended 4.5.3**: JWT authentication
- **python-dotenv 1.0.0**: Environment variable management

### Security Dependencies
- **bcrypt 4.0.1**: Password hashing
- **Werkzeug 2.3.7**: Security utilities

### Full dependency list in [`requirements.txt`](planventure-api/requirements.txt)

## 🚨 Error Handling

The API provides comprehensive error handling with consistent JSON responses:

```json
{
  "error": "Error type",
  "message": "Human-readable error description",
  "details": {
    "field": "Specific validation error"
  }
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `423`: Locked
- `500`: Internal Server Error

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests and ensure code quality
5. Commit changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- 📧 Email: opensource@github.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/planventure/issues)
- 📖 Documentation: This README and inline code comments
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/planventure/discussions)

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Update production values in `.env`
2. **Database**: Consider PostgreSQL for production
3. **Security**: Use strong secret keys and enable HTTPS
4. **CORS**: Configure specific origins for production
5. **Monitoring**: Implement logging and error tracking

### Docker Support
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## 🔄 API Versioning

Current API version: **v1**

All endpoints are prefixed with `/api` for consistency and future versioning support.

---

**Built with ❤️ using Flask and modern Python practices**