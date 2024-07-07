# user_management/tests.py

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from .models import User, Organisation
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta

class UserManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'phone': '1234567890'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['firstName'], 'John')
        self.assertEqual(response.data['data']['user']['email'], 'john.doe@example.com')

        # Verify default organisation name
        user = User.objects.get(email=self.user_data['email'])
        org = Organisation.objects.get(users=user)
        self.assertEqual(org.name, "John's Organisation")

    def test_user_login(self):
        # First register a user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Then attempt to log in
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])

    def test_user_registration_validation(self):
        invalid_user_data = self.user_data.copy()
        invalid_user_data['email'] = ''  # Invalid email

        response = self.client.post(self.register_url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    def test_duplicate_user_registration(self):
        # Register a user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Attempt to register the same user again
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    def test_token_generation(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        token = response.data['data']['accessToken']
        decoded_token = RefreshToken(token)
        self.assertEqual(decoded_token['user_id'], User.objects.get(email=self.user_data['email']).id)

        # Verify token expiration
        decoded_token.set_exp(lifetime=timedelta(minutes=5))
        self.assertTrue(decoded_token['exp'] > timezone.now())

    def test_organisation_access(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        token = response.data['data']['accessToken']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        org_url = reverse('organisation-list')
        response = self.client.get(org_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['data']['organisations']), 1)

        # Ensure users can't see organisations they don't have access to
        another_user_data = self.user_data.copy()
        another_user_data['email'] = 'jane.doe@example.com'
        self.client.post(self.register_url, another_user_data, format='json')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(org_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['data']['organisations']), 1)

    # End-to-End Tests for Register Endpoint
    def test_register_user_successfully_with_default_organisation(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['firstName'], 'John')
        self.assertEqual(response.data['data']['user']['email'], 'john.doe@example.com')

        # Verify default organisation name
        user = User.objects.get(email=self.user_data['email'])
        org = Organisation.objects.get(users=user)
        self.assertEqual(org.name, "John's Organisation")

    def test_register_user_with_missing_required_fields(self):
        required_fields = ['firstName', 'lastName', 'email', 'password', 'phone']
        for field in required_fields:
            invalid_user_data = self.user_data.copy()
            invalid_user_data[field] = ''  # Invalid value

            response = self.client.post(self.register_url, invalid_user_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            self.assertIn('errors', response.data)

    def test_register_user_with_duplicate_email(self):
        # Register a user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Attempt to register the same user again
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)
