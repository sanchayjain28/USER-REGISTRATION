from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from jose import jwt, JWTError
from models import UserBase, UserLogin
from database import db
from utils import encrypt, verify, get_current_user
from settings import settings
router = APIRouter()

@router.on_event("startup")
def startup():
    db.connect()


@router.on_event("shutdown")
def shutdown():
    db.disconnect()

@router.get("/")
def home():
    return {"message": "Hello, FastAPI!"}

@router.post("/register")
async def register_user(user: UserBase):
    existing_user = db.execute_query(
        "SELECT * FROM users WHERE email = %s;",
        (user.email,)
    )   
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists") 
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    password = encrypt(user.password)
    db.execute_query(
        "INSERT INTO users (email, first_name, last_name, password) VALUES (%s, %s, %s, %s);",
        (user.email, user.first_name, user.last_name, password)
    )

    return {"message": "User registered successfully", "status_code": 201}

 

def create_token(data, expires_delta):
    """Create a JWT token with expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings["SECRET_KEY"], algorithm=settings["ALGORITHM"])
    return encoded_jwt

@router.post("/login")
async def login_user(user: UserLogin, response: Response):
    try:
        existing_user = db.execute_query(
            "SELECT * FROM users WHERE email = %s;",
            (user.email,)
        )   
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify(user.password, existing_user[0]["password"]):
            raise HTTPException(status_code=401, detail="Incorrect password")
        user_data = {
            "sub": user.email,
            "user_id": existing_user[0]["id"]
        }
        
        access_token = create_token(
            data={**user_data, "type": "access"},
            expires_delta=timedelta(minutes=float(settings["ACCESS_TOKEN_EXPIRE_MINUTES"]))
        )
        
        refresh_token = create_token(
            data={**user_data, "type": "refresh"},
            expires_delta=timedelta(minutes=float(settings["REFRESH_TOKEN_EXPIRE_MINUTES"]))
        )
        
        response = JSONResponse(content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
        })
        print(refresh_token, access_token)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True, # cant acces through frontend
            secure=False,  # for production user True
            samesite="lax",
            max_age=float(settings["ACCESS_TOKEN_EXPIRE_MINUTES"]) * 60,
            path="/"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True, # cant acces through frontend
            secure=False,  # for production user True
            samesite="lax",
            max_age=float(settings["REFRESH_TOKEN_EXPIRE_MINUTES"]) * 60,
            path="/"
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh")
async def refresh_tokens(response: Response, refresh_token: str = None):
    """Endpoint to refresh access token using refresh token"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token required")
    
    try:
        payload = jwt.decode(refresh_token, settings["SECRET_KEY"], algorithms=[settings['ALGORITHM']])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_data = {
            "sub": payload["sub"],
            "user_id": payload["user_id"]
        }
        
        new_access_token = create_token(
            data={**user_data, "type": "access"},
            expires_delta=timedelta(minutes=float(settings["ACCESS_TOKEN_EXPIRE_MINUTES"]))
        )
        
        new_refresh_token = create_token(
            data={**user_data, "type": "refresh"},
            expires_delta=timedelta(minutes=float(settings["REFRESH_TOKEN_EXPIRE_MINUTES"]))
        )
        
        response = JSONResponse(content={
            "message": "Tokens refreshed successfully",
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        })
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True, # cant acces through frontend
            secure=False,  # for production user True
            samesite="lax",
            max_age=float(settings["ACCESS_TOKEN_EXPIRE_MINUTES"]) * 60,
            path="/"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True, # cant acces through frontend
            secure=False,  # for production user True
            samesite="lax",
            max_age=float(settings["REFRESH_TOKEN_EXPIRE_MINUTES"]) * 60,
            path="/"
        )
        
        return response
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/me")
async def get_user_details(request: Request):
    """Get details of the currently logged in user"""
    access_token = request.cookies.get("access_token")
    print(access_token)
    payload = get_current_user(access_token)
    user = db.execute_query(
        "SELECT id, email, first_name, last_name FROM users WHERE email = %s;",
        (payload.get("sub"),)
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user = user[0]
    return {
        "id": user["id"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"]
    }