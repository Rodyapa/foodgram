from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.validators import username_validator

from foodgram.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH

User = get_user_model()


class UserAuthTestCase(TestCase):
    TEST_USER_PASSWORD = 'tes_pas3'
    TEST_USER_EMAIL = 'test_user@gmail.com'

    @classmethod
    def setUp(cls):
        cls.client = APIClient()
        cls.test_user = User.objects.create(
            username='test_user',
            email=cls.TEST_USER_EMAIL,
            first_name='test',
            last_name='user',
            password=make_password(cls.TEST_USER_PASSWORD)
        )
        cls.auth_client = APIClient()
        cls.auth_client.login(
            email=cls.TEST_USER_EMAIL,
            password=cls.TEST_USER_PASSWORD
        )

    def test_request_with_correct_credential_will_create_user(self):
        """
        При предоставленнии правильных данных, юзер
        может создать экземплятр пользователя.
        """
        endpoint = '/api/users/'
        data = {
            "email": 'somemail@mail.ru',
            "username": 'someuser',
            "first_name": "Вася",
            "last_name": "Иванов",
            "password": 'Secretpas$word'
        }
        response = self.client.post(endpoint, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg='Ожидаемый статус ответа - 201.')
        user = User.objects.filter(username='someuser')
        self.assertNotEqual(user, None, msg='Пользователь не был создан')

    def test_get_token_with_correct_credentials(self):
        """
        Юзер предоставивший правильные учетные данные,
        может получить токен.
        """
        endpoint = '/api/auth/token/login/'
        data = {
            "email": self.TEST_USER_EMAIL,
            "password": self.TEST_USER_PASSWORD
        }
        response = self.client.post(path=endpoint, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Ожидаемый статус ответа: 200.')
        self.assertIn('auth_token', response.data,
                      msg='В теле ответа должен быть указан auth_token')

    def test_request_with_lack_of_credentials_doesnt_create_user(self):
        """
        При отсутсвии кокого-либо из необходимых полей,
        экземпляр юзера не будет создан.
        """
        incomplete_datas = (
            {
                "username": 'userwithnoemail',
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            },
            {
                "email": 'userwitnoname@mail.ru',
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            },
            {
                "email": 'somemail@mail.ru',
                "username": 'user_with_no_name',
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            },
            {
                "email": 'somemail@mail.ru',
                "username": 'someuser',
                "first_name": "Вася_без_фамилии",
                "password": 'Secretpas$word'
            },
            {
                "email": 'somemail@mail.ru',
                "username": 'someuser',
                "first_name": "Вася",
                "last_name": "Без Секретов",
            }
        )
        for item in incomplete_datas:
            with self.subTest():
                data = item
                endpoint = '/api/users/'
                reponse = self.client.post(endpoint, data)
                self.assertEqual(reponse.status_code,
                                 status.HTTP_400_BAD_REQUEST)

    def test_request_with_incorrect_data_wont_create_user(self):
        """
        При попытки создать пользователя с полями несоотвествующими формату,
        экземпляр пользователя не будет создан.
        """
        incorrect_datas = (
            ({
                "username": f'{"user"*MAX_USERNAME_LENGTH}',
                "email": 'userwitnoname@mail.ru',
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            }, (f'Пользователь не может задать значения поле username '
                f'больше, чем {MAX_USERNAME_LENGTH}')
            ),
            ({
                "username": 'username',
                "email": f'{"user"*MAX_EMAIL_LENGTH+"@mail.ru"}',
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            }, (f'Пользователь не может задать значения поле емейла '
                f'больше, чем {MAX_EMAIL_LENGTH}')),
            ({
                "email": 'somemail@mail.ru',
                "username": 'user_with_no_name',
                "first_name":
                f'{"Вася"*User._meta.get_field("first_name").max_length}',
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            }, (f'Пользователь не может задать значения поле имени'
                f'больше, чем {User._meta.get_field("first_name").max_length}')
            ),
            ({
                "email": 'somemail@mail.ru',
                "username": 'user_with_long_last_name',
                "first_name": "Вася",
                "last_name":
                f'{"Иванов"*User._meta.get_field("last_name").max_length}',
                "password": 'Secretpas$word'
            }, (f'Пользователь не может задать значения поле фамилии'
                f'больше, чем {User._meta.get_field("last_name").max_length}')
            ),
            ({
                "email": 'somemail@mail.ru',
                "username": 'username$',
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            }, (f'Пользователь не может задать значения поле имени'
                f' не соответсвующее регулярному выражению:'
                f'{username_validator.regex}')
            ),
            ({
                "email": f'{self.TEST_USER_EMAIL}',
                "username": 'user_with_used_email',
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            }, ('Пользователь не может создать пользователя с почтой,'
                ' которая уже используется')
            ),
            ({
                "email": 'somemail@mail.ru',
                "username": 'test_user',
                "first_name": "Вася",
                "last_name": "Иванов",
                "password": 'Secretpas$word'
            }, ('Пользователь не может создать пользователя с username,'
                ' который уже используется')
            )
        )
        for item in incorrect_datas:
            with self.subTest():
                data, msg = item
                endpoint = '/api/users/'
                response = self.client.post(endpoint, data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST,
                                 msg)

    def test_get_token_bad_requests(self):
        """
        Пользователь не может получить токен,
        предоставив неверные данные
        """
        incomplete_datas = (
            ({
                "email": f"{self.test_user.email}",
                "password": "randompassword"
            }, 'При указании неправильного пароля - токен не будет возвращен'
            ),
            ({
                "password": f"{self.test_user.password}"
            }, 'При отсуствии емейла в запросе - токен не будет возвращен'
            ),
            ({
                "email": f"{self.test_user.email}",
            }, 'При отсуствии пароля в запросе - токен не будет возвращен'
            )
        )
        for item in incomplete_datas:
            data, msg = item
            with self.subTest():
                endpoint = '/api/auth/token/login/'
                reponse = self.client.post(endpoint, data)
                self.assertEqual(reponse.status_code,
                                 status.HTTP_400_BAD_REQUEST,
                                 msg)

    def test_logout(self):
        """
        Пользователь может создать токен, затем удалить его и снова создать.
        """
        endpoint = '/api/auth/token/login/'
        data = {
            "email": self.TEST_USER_EMAIL,
            "password": self.TEST_USER_PASSWORD
        }
        response = self.auth_client.post(endpoint, data,)
        auth_token = response.data.get('auth_token')
        endpoint_logout = '/api/auth/token/logout/'
        self.auth_client.credentials(HTTP_AUTHORIZATION='Token ' + auth_token)
        response = self.auth_client.post(endpoint_logout)
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)
