from pydantic import BaseModel
from pydantic import EmailStr


class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class GetOTP(BaseModel):
    email: EmailStr

class SendOTP(BaseModel):
    email: EmailStr
    otp: str