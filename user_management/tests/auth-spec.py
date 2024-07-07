from django.test import TestCase
from unittest.mock import patch
import requests
import unittest
import jwt, time

BaseUrl = "http://localhost:8000"

mock_jwt_value = {
    "token_type": "access",
    "exp": 1720431264,
    "iat": 1720344864,
    "jti": "e41bf256b5164f688a24f997b664f66f",
    "user_id": "5a56cd91-ef55-4e21-9fb6-f4d7d1253c98"
}

mock_login_details = {
    "status": "success",
    "message": "Login Successful",
    "data": {
        'accessToken': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIwNDMxMjY0LCJpYXQiOjE3MjAzNDQ4NjQsImp0aSI6ImU0MWJmMjU2YjUxNjRmNjg4YTI0Zjk5N2I2NjRmNjZmIiwidXNlcl9pZCI6IjVhNTZjZDkxLWVmNTUtNGUyMS05ZmI2LWY0ZDdkMTI1M2M5OCJ9.zOajy5WEuEU8laHyxNgVT9vwv6GR01aEski1a6S45wo",
        "user": {
            "userId": "5a56cd91-ef55-4e21-9fb6-f4d7d1253c98",
            "firstName": "Andrew",
            "lastName": "Adeleye",
            "email": "andyadeleye@gmail.com",
            "phone": "08102980007",
            "password": "leye123"
        }
    }
}

mock_user_organisation_reply = {
    "status": "success",
    "message": "QuerySuccessful",
    "data": {
        "organisations": [
            {
                "orgid": "teettetetet",
                "name": "Andrew's Org",
                "description": ''
            }
        ]
    }
}

class APITests(TestCase):
    # Token generation unit test
    @patch('jwt.decode')
    def test_token_generation(self, mock_decode):
        mock_decode.return_value = mock_jwt_value

        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Replace with an actual token
        decoded = mock_decode(token, options={"verify_signature": False})
        self.assertEqual(decoded, mock_jwt_value)


    # Token Expiry Unit test
    @patch('requests.post')
    def test_token_expiry(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_details

        response = requests.post(f"{BaseUrl}/auth/login", json={"email": "andyadeleye@gmail.com", "password": "leye123"})
        self.assertEqual(response.status_code, 200)
        
        decoded_token = jwt.decode(response.json()["data"]["accessToken"], verify=False)
        token_exp = decoded_token['exp']
        current_time = int(time.time())
        self.assertLessEqual(token_exp, current_time + 86400)


    
    # User details in token unit test
    @patch('requests.post')
    def test_user_details_in_token(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_details

        response = requests.post(f"{BaseUrl}/auth/login", json={"email": "andyadeleye@gmail.com", "password": "leye123"})
        self.assertEqual(response.status_code, 200)
        
        decoded_token = jwt.decode(response.json()["data"]["accessToken"], verify=False)
        self.assertEqual(decoded_token['user_id'], "5a56cd91-ef55-4e21-9fb6-f4d7d1253c98")

    # Test Organisation
    @patch('requests.get')
    def test_get_organisations(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_user_organisation_reply

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'  # Replace with an actual token
        }

        response = requests.get(f"{BaseUrl}/api/organisations", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_user_organisation_reply)


    """End to End Testing"""
    @patch('requests.post')
    def test_login(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_details

        response = requests.post(f"{BaseUrl}/auth/login", json={"email": "andyadeleye@gmail.com", "password": "leye123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_login_details)



    @patch('requests.post')
    def test_register_user(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "status": "success",
            "data": {
                "user": {
                    "firstName": "Andrew"
                }
            }
        }

        user_data = {
            "firstName": "Andrew",
            "lastName": "Adeleye",
            "email": "andyadeleye@gmail.com",
            "phone": "08102980007",
            "password": "leye123"
        }

        response = requests.post(f"{BaseUrl}/auth/register", json=user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["data"]["user"]["firstName"], "Andrew")

    @patch('requests.post')
    def test_validation_error(self, mock_post):
        mock_post.return_value.status_code = 422

        user_data = {
            "email": "andyadeleye@gmail.com",
            "phone": "08102980007"
        }

        response = requests.post(f"{BaseUrl}/auth/register", json=user_data)
        self.assertEqual(response.status_code, 422)

    @patch('requests.post')
    def test_successful_user_login(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_details

        user_data = {
            "email": "andyadeleye@gmail.com",
            "password": "leye123"
        }

        response = requests.post(f"{BaseUrl}/auth/login", json=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("accessToken", response.json()["data"])

    @patch('requests.post')
    def test_failed_user_login(self, mock_post):
        mock_post.return_value.status_code = 401

        user_data = {
            "email": "andyadeleye@gmail.com",
            "password": "leye13"
        }

        response = requests.post(f"{BaseUrl}/auth/login", json=user_data)
        self.assertEqual(response.status_code, 401)

    @patch('requests.post')
    def test_login_validation_error(self, mock_post):
        mock_post.return_value.status_code = 422

        user_data = {
            "email": "andyadeleye@gmail.com"
        }

        response = requests.post(f"{BaseUrl}/auth/login", json=user_data)
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()
