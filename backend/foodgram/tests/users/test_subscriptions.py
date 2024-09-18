from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from tests.base_test import BaseTestCase
from users.models import Subscription

UserModel = get_user_model()


class UserSubscriptionsTestCase(BaseTestCase):
    BASE_URL = '/api/users/subscriptions/'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.auth_client_2 = APIClient()
        cls.user_authenticated_2 = UserModel.objects.create_user(
            username='auth_user_2', password='password',
            first_name='second_user', last_name='second_user',
            email='user2mail@gmail.com'
        )
        token = Token.objects.create(user=cls.user_authenticated_2)
        cls.auth_client_2.credentials(
            HTTP_AUTHORIZATION='Token ' + token.key)

    def test_user_can_get_list_of_subscriptions(self):
        # Arrange
        Subscription.objects.create(user=self.user_authenticated_1,
                                    target_user=self.user_authenticated_2)
        test_cases = [
            (self.auth_client_1, 200,
             'User should be able to get list of his subscriptons'),
            (self.client, 401,
             'Anonymous User should not be albe to get list of subscriptions')
        ]

        # Act
        for client, expected_status, error_msg in test_cases:
            with self.subTest(client=client, error_msg=error_msg,
                              expected_status=expected_status):
                response = client.get(self.BASE_URL)
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)
                if expected_status == 200:
                    self.assertNotIn(
                        'password', response.data,
                        'List of user infos can not contains passwords')

    def test_subscription_creating(self):
        # Arrange
        second_user_id = self.user_authenticated_2.id
        correct_url = f'/api/users/{second_user_id}/subscribe/'
        non_existing_user_url = '/api/users/999/subscribe/'

        test_cases = [
            (self.auth_client_1, 201, correct_url,
             'User should be able to make a subscripton'),
            (self.client, 401, correct_url,
             'Anonymous User should not be albe to make a subscription'),
            (self.auth_client_1, 404, non_existing_user_url,
             'Attemt to subscribe to non existing user should return 404')
        ]

        # Act
        for client, expected_status, url, error_msg in test_cases:
            with self.subTest(client=client, error_msg=error_msg,
                              expected_status=expected_status):
                response = client.post(url)
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)

    def test_subscription_canceling(self):
        # Arrange
        Subscription.objects.create(user=self.user_authenticated_1,
                                    target_user=self.user_authenticated_2)

        second_user_id = self.user_authenticated_2.id
        correct_url = f'/api/users/{second_user_id}/subscribe/'
        non_existing_user_url = '/api/users/999/subscribe/'

        test_cases = [
            (self.auth_client_1, 204, correct_url,
             'User should be able to cancel a subscripton'),
            (self.client, 401, correct_url,
             'Anonymous User should not be albe to cancel a subscription'),
            (self.auth_client_1, 404, non_existing_user_url,
             'Attemt to cancel subscription to non existing '
             'user should return 404')
        ]

        # Act
        for client, expected_status, url, error_msg in test_cases:
            with self.subTest(client=client, error_msg=error_msg,
                              expected_status=expected_status):
                response = client.delete(url)
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)
