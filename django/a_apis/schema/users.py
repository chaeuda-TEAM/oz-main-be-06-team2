from typing import Optional

from ninja import Schema


class SignupSchema(Schema):
    username: str
    user_id: str
    password: str
    password_confirm: str
    phone_number: str
    email: str


class LoginSchema(Schema):
    email: str
    password: str


class TokenSchema(Schema):
    access: str
    refresh: str


class UserSchema(Schema):
    email: str


class UserResponseSchema(Schema):
    email: str
    username: str
    user_id: str


class AuthResponseSchema(Schema):
    success: bool
    message: str
    tokens: Optional[TokenSchema] = None
    user: Optional[UserResponseSchema] = None


class RefreshTokenSchema(Schema):
    refresh: str


class TokenResponseSchema(Schema):
    success: bool
    message: str
    tokens: Optional[TokenSchema] = None
