import json
from datetime import timedelta

from a_apis.models.email_verification import EmailVerification
from a_user.models import User

from django.test import Client, TestCase
from django.utils import timezone


class UserAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "test@example.com"
        self.password = "testpass123"
        self.username = "testuser"
        self.phone_number = "010-1234-5678"

        # 기본 요청 데이터 설정
        self.signup_data = {
            "email": self.email,
            "password": self.password,
            "username": self.username,
            "phone_number": self.phone_number,
        }

        self.login_data = {
            "email": self.email,
            "password": self.password,
        }

        # Create verified email verification
        self.create_verified_email()

    def create_verified_email(self):
        """이메일 인증 데이터 생성 헬퍼 메서드"""
        return EmailVerification.objects.create(
            email=self.email,
            is_verified=True,
            expires_at=timezone.now() + timedelta(minutes=30),
            verification_code="123456",
        )

    def create_user_and_get_tokens(self):
        """사용자 생성 및 토큰 반환 헬퍼 메서드"""
        response = self.client.post(
            "/api/users/signup",
            data=json.dumps(self.signup_data),
            content_type="application/json",
        )
        return json.loads(response.content.decode())

    def test_signup_success(self):
        """정상적인 회원가입 테스트"""
        response = self.client.post(
            "/api/users/signup",
            data=json.dumps(self.signup_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode())

        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "회원가입이 완료되었습니다.")
        self.assertIn("tokens", response_data)
        self.assertIn("user", response_data)

        # 사용자 생성 확인
        user = User.objects.get(email=self.email)
        self.assertEqual(user.username, self.username)

    def test_login_success(self):
        """정상적인 로그인 테스트"""
        # 사용자 생성
        self.create_user_and_get_tokens()

        response = self.client.post(
            "/api/users/login",
            data=json.dumps(self.login_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode())

        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "로그인 되었습니다.")
        self.assertIn("tokens", response_data)
        self.assertIn("user", response_data)

    def test_login_invalid_credentials(self):
        data = {
            "email": "nonexistent@example.com",
            "password": "wrongpass",
        }

        response = self.client.post(
            "/api/users/login", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode())
        self.assertFalse(response_data["success"])
        self.assertEqual(
            response_data["message"], "이메일 또는 비밀번호가 잘못되었습니다."
        )

    def test_refresh_token(self):
        # First login to get tokens
        self.test_signup()
        login_data = {
            "email": self.email,
            "password": self.password,
        }
        login_response = self.client.post(
            "/api/users/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        login_response_data = json.loads(login_response.content.decode())
        refresh_token = login_response_data["tokens"]["refresh"]

        # Try to refresh token
        refresh_data = {
            "refresh": refresh_token,
        }
        response = self.client.post(
            "/api/users/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode())
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "토큰이 갱신되었습니다.")
        self.assertIn("tokens", response_data)

    def test_logout(self):
        # First login to get tokens
        self.test_signup_success()
        login_data = {
            "email": self.email,
            "password": self.password,
        }
        login_response = self.client.post(
            "/api/users/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        login_response_data = json.loads(login_response.content.decode())
        refresh_token = login_response_data["tokens"]["refresh"]

        # Try to logout
        logout_data = {
            "refresh_token": refresh_token,
        }
        response = self.client.post(
            "/api/users/logout",
            data=json.dumps(logout_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode())
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "로그아웃 되었습니다.")

    def test_signup_without_email_verification(self):
        # Delete email verification
        EmailVerification.objects.all().delete()

        data = {
            "email": self.email,
            "password": self.password,
            "username": self.username,
            "phone_number": self.phone_number,
        }

        response = self.client.post(
            "/api/users/signup", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode())
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["message"], "이메일 인증이 필요합니다.")
