from pydantic import BaseModel, Field
from uuid import UUID


class UserCreate(BaseModel):
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class UserRegisterResponse(BaseModel):
    id: UUID = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserLoginResponse(BaseModel):
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type")
    user_id: UUID = Field(..., description="User ID")

    class Config:
        from_attributes = True
