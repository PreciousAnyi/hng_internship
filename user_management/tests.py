# usermanagement/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'firstName': 'Test',
            'lastName': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.login_url = reverse('login')
    
    def test_login_with_email(self):
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], self.user_data['email'])

    def test_login_with_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'Bad request')
        self.assertEqual(response.data['message'], 'Authentication failed')

    def test_login_with_nonexistent_email(self):
        response = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': self.user_data['password']
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'Bad request')
        self.assertEqual(response.data['message'], 'Authentication failed')
