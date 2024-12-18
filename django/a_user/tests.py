from a_user.models import User

from django.test import Client, TestCase
from django.urls import reverse


class UserAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        response = self.client.post(
            "/api/users/signup",
            {
                "email": "test@example.com",
                "password": "testpass123",
                "nickname": "testuser",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
