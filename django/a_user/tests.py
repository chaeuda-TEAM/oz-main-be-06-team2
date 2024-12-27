import json
from datetime import timedelta

from a_apis.models.email_verification import EmailVerification
from a_user.models import User

from django.test import Client, TestCase
from django.utils import timezone


class UserAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create verified email verification record
        self.email = "test@example.com"
        EmailVerification.objects.create(
            email=self.email,
            is_verified=True,
            expires_at=timezone.now() + timedelta(minutes=30),
            verification_code="123456",
        )

    def test_signup(self):
        # Verify email verification record exists
        verification = EmailVerification.objects.filter(
            email=self.email, is_verified=True
        ).first()
        print("Email verification exists:", verification is not None)
        print("Email verification object:", verification)

        data = {
            "email": self.email,
            "password": "testpass123",
            "username": "testuser",
            "user_id": "testuser123",
            "phone_number": "010-1234-5678",
        }

        print("Request data:", data)

        response = self.client.post(
            "/api/users/signup", data=json.dumps(data), content_type="application/json"
        )

        print("Response status:", response.status_code)
        print("Response content:", response.content.decode())

        try:
            response_data = json.loads(response.content.decode())
            print("Response data:", response_data)
            if not response_data["success"]:
                print("Error message:", response_data["message"])
        except json.JSONDecodeError as e:
            print("Failed to parse response JSON:", e)

        # Assert response status code
        self.assertEqual(response.status_code, 200)

        # Assert user was created
        user = User.objects.filter(email=self.email).first()
        print("User object:", user)
        print("All users:", User.objects.all())
        self.assertIsNotNone(user)

        # Assert response structure
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], "회원가입이 완료되었습니다.")
        self.assertIn("tokens", response_data)
        self.assertIn("user", response_data)

        # Assert user data in response
        self.assertEqual(response_data["user"]["email"], self.email)
        self.assertEqual(response_data["user"]["username"], data["username"])
        self.assertEqual(response_data["user"]["user_id"], data["user_id"])

        # Assert tokens are present
        self.assertIn("access", response_data["tokens"])
        self.assertIn("refresh", response_data["tokens"])
