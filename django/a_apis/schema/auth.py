from ninja import Schema


class GoogleLoginSchema(Schema):
    token_id: str


class AuthMessages:
    GOOGLE_LOGIN_SUCCESS = "Google 로그인 성공"
    EMAIL_NOT_VERIFIED = "이메일이 인증되지 않았습니다."
    INVALID_GOOGLE_TOKEN = "유효하지 않은 Google 토큰입니다."
    SERVER_ERROR = "서버 오류: {}"
