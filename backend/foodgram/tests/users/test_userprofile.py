from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class ProfileAvatarEditTestCase(TestCase):
    '''
    Test actions related to profile avatar.
    '''
    URL = '/api/users/me/avatar/'

    @classmethod
    def setUpTestData(cls):  # Arrange data for entire test suite.
        # Create Users
        cls.unauth_client = APIClient()
        cls.auth_client_1 = APIClient()

        cls.user_authencticated_1 = UserModel.objects.create_user(
            username='auth_user_1', password='password',
            first_name='first_user', last_name='first_user',
            email='user1mail@gmail.com')
        cls.token = Token.objects.create(user=cls.user_authencticated_1)
        cls.auth_client_1.credentials(
            HTTP_AUTHORIZATION='Token ' + cls.token.key)

    def test_authorized_user_can_add_avatar(self):
        # Assert
        payload = {
            "avatar": ("data:image/png;base64,"
                       "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg"
                       "MAAABieywaAAAACVBMVEUAAAD///9fX1/S0"
                       "ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAC"
                       "klEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==")
            }

        # Act
        response = self.auth_client_1.put(
            self.URL,
            payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, 200,
                         'User should be able to add profile avatar. \n'
                         'Avatar should be encoded into Base64')
        self.assertIn('avatar', response.data,
                      'There must be uploaded avatar in response data.')

    def test_user_cannot_create_avatar_with_wrong_data(self):
        # Assert
        payload = {
            "avatar": ("wrong_data")
            }

        # Act
        response = self.auth_client_1.put(
            self.URL,
            payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, 400,
                         'User cannot create avatar with wrong data.')

    def test_unauthorized_user_cannot_add_avatar(self):
        # Assert
        payload = {
            "avatar": ("data:image/png;base64,"
                       "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg"
                       "MAAABieywaAAAACVBMVEUAAAD///9fX1/S0"
                       "ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAC"
                       "klEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==")
            }

        # Act
        response = self.unauth_client.put(
            self.URL,
            payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, 401,
                         'Anonymous should not be able to add profile avatar.')

    def test_authorized_user_can_delete_his_avatar(self):
        # Act
        response = self.auth_client_1.delete(
            self.URL
        )

        # Assert
        self.assertEqual(response.status_code, 204,
                         'Authorized User should be able to delete '
                         'profile avatar.')

    def test_anonymous_cannot_delete_avatar(self):
        # Act
        response = self.unauth_client.delete(
            self.URL
        )

        # Assert
        self.assertEqual(response.status_code, 401,
                         'Anonymous should receive 401 status code')


class EditPasswordTestCase(TestCase):
    URL = '/api/users/set_password/'

    @classmethod
    def setUpTestData(cls):  # Arrange data for entire test suite.
        # Create Users
        cls.unauth_client = APIClient()
        cls.auth_client_1 = APIClient()
        cls.user_authencticated_1 = UserModel.objects.create_user(
            username='auth_user_1', password='password',
            first_name='first_user', last_name='first_user',
            email='user1mail@gmail.com')
        cls.token = Token.objects.create(user=cls.user_authencticated_1)
        cls.auth_client_1.credentials(
            HTTP_AUTHORIZATION='Token ' + cls.token.key)

    def test_user_can_change_his_own_password(self):
        # Arrange
        payload = {
            "new_password": "string123",
            "current_password": "password"
            }

        # Act
        response = self.auth_client_1.post(
            self.URL,
            payload,
            format='json'
        )
        # Assert
        self.assertEqual(response.status_code, 204,
                         f'{response.data}'
                         'User should be able to change his password')

    def test_user_cannot_change_password_with_wrong_data(self):
        # Arrange
        wrong_datas = [{
                "new_password": "string123",
                "current_password": "wrong_current_password"
            },
            {
                "new_password": "short",
                "current_password": "password"
            }]
        # Act
        for payload in wrong_datas:
            with self.subTest(payload=payload):
                response = self.auth_client_1.post(
                    self.URL,
                    payload,
                    format='json'
                )
                # Assert
                self.assertEqual(
                    response.status_code, 400,
                    f'{payload} \n'
                    'User should not be able password with wrong data')

    def test_anonymous_cannot_change_his_own_password(self):
        # Arrange
        payload = {
            "new_password": "string123",
            "current_password": "password"
            }

        # Act
        response = self.unauth_client.post(
            self.URL,
            payload,
            format='json'
        )
        # Assert
        self.assertEqual(response.status_code, 401,
                         f'{response.data}'
                         'Anonymous cannot change his password')


class GetUserInfoTestCase(TestCase):
    BASE_URL = '/api/users/'

    @classmethod
    def setUpTestData(cls):  # Arrange data for entire test suite.
        # Create Users
        cls.unauth_client = APIClient()
        cls.auth_client_1 = APIClient()
        cls.user_authencticated_1 = UserModel.objects.create_user(
            username='auth_user_1', password='password',
            first_name='first_user', last_name='first_user',
            email='user1mail@gmail.com')
        cls.token = Token.objects.create(user=cls.user_authencticated_1)
        cls.auth_client_1.credentials(
            HTTP_AUTHORIZATION='Token ' + cls.token.key)

    def test_anyone_can_get_list_of_users(self):
        # Act
        response = self.unauth_client.get(self.BASE_URL)

        # Assert
        self.assertEqual(response.status_code, 200,
                         'Anonymous must be able to get list of users')
        self.assertIn('results', response.data,
                      'Response must contain "results" key with user infos')
        self.assertNotIn('password', response.data['results'][0].keys(),
                         'List of user infos can not contains passwords')

    def test_anyone_can_get_specific_user_info(self):
        # Act
        response = self.unauth_client.get(self.BASE_URL + '1/')

        # Assert
        self.assertEqual(response.status_code, 200,
                         'Anonymous must be able to get specific user info')

        self.assertNotIn('password', response.data.keys(),
                         'User info can not contain password')

    def test_attempt_to_get_nonexistent_user_receives_404(self):
        # Act
        response = self.unauth_client.get(self.BASE_URL + '9999/')

        # Assert
        self.assertEqual(response.status_code, 404,
                         'Attempt to get nonexistent user receives 404')

    def test_authenticated_user_can_receive_his_own_info(self):
        # Act
        response = self.auth_client_1.get(self.BASE_URL + 'me/')

        # Assert
        self.assertEqual(response.status_code, 200,
                         'Authorized user can his own info.')
        self.assertEqual(response['Content-Type'], 'application/json',
                         'Response must be in Json format')

    def test_anonymous_cannot_receive_his_own_info(self):
        # Act
        response = self.unauth_client.get(self.BASE_URL + 'me/')

        # Assert
        self.assertEqual(response.status_code, 401,
                         'Anonymous can not get his own info.')
