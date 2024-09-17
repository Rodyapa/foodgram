from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
UserModel = get_user_model()


class BaseTestCase(TestCase):
    '''
    Provide prearranged Authorized and Anonymous Test Clients.
    Use this class in purpose to follow DRY concept.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.unauth_client = APIClient()
        cls.auth_client_1 = APIClient()

        cls.user_authenticated_1 = UserModel.objects.create_user(
            username='auth_user_1', password='password',
            first_name='first_user', last_name='first_user',
            email='user1mail@gmail.com'
        )
        cls.token = Token.objects.create(user=cls.user_authenticated_1)
        cls.auth_client_1.credentials(
            HTTP_AUTHORIZATION='Token ' + cls.token.key)
