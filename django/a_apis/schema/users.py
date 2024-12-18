from typing import Optional

from ninja import Schema


class SignupSchema(Schema):
    email: str
    password: str
    nickname: str = None


class LoginSchema(Schema):
    email: str
    password: str


class TokenSchema(Schema):
    access: str
    refresh: str


class UserSchema(Schema):
    email: str


class AuthResponseSchema(Schema):
    success: bool
    message: str
    tokens: Optional[TokenSchema] = None
    user: Optional[UserSchema] = None


class RefreshTokenSchema(Schema):
    refresh: str


class TokenResponseSchema(Schema):
    success: bool
    message: str
    tokens: Optional[TokenSchema] = None
