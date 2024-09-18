from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from tests.base_test import BaseTestCase

UserModel = get_user_model()


class ProfileAvatarEditTestCase(BaseTestCase):
    '''
    Test actions related to profile avatar.
    '''
    URL = '/api/users/me/avatar/'
    VALID_AVATAR = ("data:image/png;base64,"
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg"
                    "MAAABieywaAAAACVBMVEUAAAD///9fX1/S0"
                    "ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAC"
                    "klEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==")
    INVALID_AVATAR = 'wrong_avatar'

    def test_avatar_creation(self):
        # Arrange
        test_cases = [
            (self.auth_client_1, 200, self.VALID_AVATAR,
             'authorized user should be able to add avatar'),
            (self.unauth_client, 401, self.VALID_AVATAR,
             'unauthorized user should not be able to add avatar'),
            (self.auth_client_1, 400, self.INVALID_AVATAR,
             'user with wrong avatar data should receive 400 response')
        ]
        # Act
        for client, expected_status, avatar_data, error_msg in test_cases:
            with self.subTest(client=client, avatar_data=avatar_data,
                              expected_status=expected_status,
                              error_msg=error_msg):
                payload = {"avatar": avatar_data}
                response = client.put(self.URL, payload, format='json')
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)

    def test_avatar_deleting(self):
        test_cases = [
            (self.auth_client_1, 204,
             'authorized user should be able to delete his avatar'),
            (self.unauth_client, 401,
             'unauthorized user should not be able to delete his avatar')
        ]
        for client, expected_status, error_msg in test_cases:
            with self.subTest(client=client,
                              expected_status=expected_status,
                              error_msg=error_msg):
                response = client.delete(self.URL)
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)


class EditPasswordTestCase(BaseTestCase):
    URL = '/api/users/set_password/'

    def test_password_changing_with_correct_credentials(self):
        # Arrange 
        test_cases = [
            (self.auth_client_1, 204,
             'Authorized User should be albe to change his password.'),
            (self.unauth_client, 401,
             'Anonymous can not change his password.'),
        ]
        payload = {
            "new_password": "string123",
            "current_password": "password"
        }
        # Act
        for client, expected_status, error_msg in test_cases:
            with self.subTest(client=client, expected_status=expected_status,
                              error_msg=error_msg):
                response = client.post(
                    self.URL,
                    payload,
                    format='json'
                )
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)

    def test_password_changing_with_wrong_data(self):
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


class GetUserInfoTestCase(BaseTestCase):
    BASE_URL = '/api/users/'

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
