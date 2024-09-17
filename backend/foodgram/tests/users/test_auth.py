from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tests.base_test import BaseTestCase

UserModel = get_user_model()


class TokenTestCase(BaseTestCase):
    '''
    Test endpoints related to the auth token.
    '''

    def test_obtain_token(self):
        '''User can provide credentails and get token in response'''
        #  Act
        response = self.auth_client_1.post(
            '/api/auth/token/login',
            {'email': 'user1mail@gmail.com', 'password': 'password'})

        #  Assert
        self.assertEqual(response.status_code, 200,
                         'User with correct credentials '
                         'should recieve 200 response')
        self.assertIn('auth_token', response.data)

    def test_cannot_obtain_token_with_wrong_credentials(self):
        '''User with wrong credentails will recieve 400 error.'''
        #  Act
        url = '/api/auth/token/login'
        response = self.auth_client_1.post(
            url,
            {'email': 'user1mail@gmail.com', 'password': 'tooshort'})

        #  Assert
        self.assertEqual(response.status_code, 400,
                         'User with incorrect credentials '
                         'should recieve 400 response')

    def test_token_deleting(self):
        # Arrange
        url = '/api/auth/token/logout/'
        test_cases = [
            (self.auth_client_1, 204,
             'User should be able to delete his token'),
            (APIClient(), 401,
             'Anonymous user should receive 401 response')
        ]
        # Act
        for client, expected_status, error_msg in test_cases:
            with self.subTest(client=client, expected_status=expected_status,
                              error_msg=error_msg):
                response = client.post(url)
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)


class RegisterTestCase(BaseTestCase):
    '''
    Tests related to registering a new user.
    '''

    def test_new_user_creation(self):
        # Arrange
        correct_credentials = {
                "email": "vpupkin@yandex.ru",
                "username": "vasya.pupkin",
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": "1234qrty"
            }
        incorrect_credentials = {
                "email": "vpupkin@yandex.ru",
                "username": "vasya.pupkin",
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": "short"
            }
        url = '/api/users/'
        test_cases = [
            (correct_credentials, 201,
             'User with correct credentials should be able to can sign in'
             ),
            (incorrect_credentials, 400,
             'User with incorrect credentials should not be able to sign in'
             )
        ]
        # Act
        for credentials, expected_status, error_message in test_cases:
            with self.subTest(credentials=credentials,
                              expected_status=expected_status,
                              error_message=error_message):
                response = self.unauth_client.post(
                    url, credentials
                )
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_message)
