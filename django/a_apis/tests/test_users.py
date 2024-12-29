import json
from datetime import timedelta

from a_apis.models.email_verification import EmailVerification
from a_user.models import User

from django.test import Client, TestCase
from django.utils import timezone


class UserLoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "test@example.com"
        self.password = "testpass123"
        self.username = "testuser"

        # 이메일 인증 생성
        self.verification = EmailVerification.objects.create(
            email=self.email,
            is_verified=True,
            expires_at=timezone.now() + timedelta(minutes=30),
            verification_code="123456",
        )

        # 테스트 유저 생성
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            is_email_verified=True,
        )

    def test_login_success(self):
        """정상적인 로그인 테스트"""
        data = {"email": self.email, "password": self.password}

        response = self.client.post(
            "/api/users/login", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)

        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "로그인 되었습니다.")
        self.assertIn("tokens", response_data)
        self.assertIn("user", response_data)
        self.assertEqual(response_data["user"]["email"], self.email)
        self.assertEqual(response_data["user"]["username"], self.username)
