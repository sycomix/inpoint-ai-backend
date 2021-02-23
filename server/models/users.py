from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import status


class User(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    email: Optional[EmailStr] = Field(None)
    full_name: Optional[str] = Field(None)
    disabled: bool = Field(False)

    class Config:
        schema_extra = {
            'example': {
                'username': 'john_doe',
                'password': 'secret',
                'email': 'johndoe@example.com',
                'full_name': 'John Doe',
                'disabled': False
            }
        }


class UserInDB(BaseModel):
    username: str = Field(...)
    hashed_password: str = Field(...)
    email: Optional[EmailStr] = Field(None)
    full_name: Optional[str] = Field(None)
    disabled: bool = Field(False)

    class Config:
        schema_extra = {
            'example': {
                'username': 'john_doe',
                'hashed_password': '$2b$12$wu6VcUjxa7NiM94QNX8bpebjJqk6NJ6vLuBnCpJ73Xy3F46eH8v0i',
                'email': 'johndoe@example.com',
                'full_name': 'John Doe',
                'disabled': False,
            }
        }


class UpdateUserModel(BaseModel):
    username: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    full_name: Optional[str] = Field(None)

    class Config:
        schema_extra = {
            'example': {
                'username': 'john_doe',
                'email': 'johndoe@example.com',
                'full_name': 'John Doe'
            }
        }


class ChangePasswordModel(BaseModel):
    password: str = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'password': 'example'
            }
        }
