**User Registration System**
-A FastAPI-based user registration and authentication system with JWT token support and cookie-based token storage.

**Features**

  User Registration with secure password hashing
  User Login with JWT Authentication
  JWT Access Token (1-minute expiration)
  JWT Refresh Token (15 days expiration)
  HTTP Cookie-based token storage
  Protected routes with JWT verification
  PostgreSQL database 
  Docker and Docker Compose 
  Environment-based configuration

**Tech Stack**

  Python 3.11
  FastAPI
  PostgreSQL


Making Docker Image -
docker build -t USER -f Dockerfile.userRegistration .

docker-compose up -d
    
