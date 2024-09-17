from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

UserModel = get_user_model()


class TokenTestCase(TestCase):
    '''
    Test endpoints related to the auth token.'''
    @classmethod
    def setUpTestData(cls):
        # Create User
        cls.auth_client_1 = APIClient()

        cls.user_authencticated_1 = UserModel.objects.create_user(
            username='auth_user_1', password='password',
            first_name='first_user', last_name='first_user',
            email='user1mail@gmail.com')

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

    def test_authenticated_user_can_delete_his_token(self):
        # Arrange
        token_obtain_response = (self.auth_client_1.post(
            '/api/auth/token/login',
            {'email': 'user1mail@gmail.com', 'password': 'password'}))
        token = token_obtain_response.data['auth_token']
        self.auth_client_1.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        # Act
        url = '/api/auth/token/logout/'
        response = self.auth_client_1.post(url)

        # Assert
        self.assertEqual(response.status_code, 204,
                         f'{response.content}'
                         'User should be able to delete his token')

        # TearDown
        self.auth_client_1.credentials()

    def test_anonymous_user_cannot_delete_his_token(self):

        # Act
        url = '/api/auth/token/logout/'
        response = self.auth_client_1.post(url)

        # Assert
        self.assertEqual(response.status_code, 401,
                         f'{response.content}'
                         'Anonymous user should receive 401 response')


class RegisterTestCase(TestCase):
    '''
    Tests related to registering a new user.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.unauth_client = APIClient()

    def test_can_create_new_user_with_correct_credentials(self):
        # Act
        response = self.unauth_client.post(
            '/api/users/',
            {
                "email": "vpupkin@yandex.ru",
                "username": "vasya.pupkin",
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": "1234qrty"
            }
        )
        self.assertEqual(response.status_code,
                         201,
                         f'{response.content}'
                         'User with correct credentials '
                         'can sign in')

    def test_cannot_create_new_user_with_incorrect_credentials(self):
        # Act
        response = self.unauth_client.post(
            '/api/users/',
            {
                "email": "vpupkin@yandex.ru",
                "username": "vasya.pupkin",
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": "short"
            }
        )
        self.assertEqual(response.status_code,
                         400,
                         f'{response.content}'
                         'User with incorrect credentials '
                         'should not be able to sign in')
