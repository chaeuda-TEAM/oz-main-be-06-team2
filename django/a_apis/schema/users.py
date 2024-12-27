from typing import Optional

from ninja import Schema


class EmailVerificationRequestSchema(Schema):
    email: str


class SignupSchema(Schema):
    username: str
    password: str
    phone_number: str
    email: str


class LoginSchema(Schema):
    user_id: str
    password: str


class TokenSchema(Schema):
    access: str
    refresh: str


class UserSchema(Schema):
    email: str


class UserResponseSchema(Schema):
    email: str
    username: str


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


class WithdrawalSchema(Schema):
    password: str


class EmailVerificationSchema(Schema):
    email: str
    code: str


class LogoutSchema(Schema):
    refresh_token: str


class ErrorResponseSchema(Schema):
    success: bool
    message: Optional[str] = None
