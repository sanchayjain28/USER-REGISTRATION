from fastapi import HTTPException
from jose import jwt, JWTError 
import hashlib

from settings import settings


def encrypt(password: str) -> str:
    salted = f"{password}{settings['HASH_KEY']}"

    hashed = hashlib.sha256(salted.encode()).hexdigest()
    return hashed

def verify(plain_password: str, hashed_password: str) -> bool:
    check_hash = encrypt(plain_password)
    
    return check_hash == hashed_password


def get_current_user(access_token: str = None):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )
    try:
        payload = jwt.decode(
            token=access_token,
            key=settings["SECRET_KEY"],
            algorithms=[settings["ALGORITHM"]]
        )
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401, 
                detail="Invalid token type"
            )
    
        return payload 
        
    except JWTError as e:
        print(e)
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="An error occurred while validating access token"
        )