# Models
from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    email: str
    password: str