from django.contrib.auth import get_user_model
from django.urls import reverse
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from tests.base_test import BaseTestCase

UserModel = get_user_model()


class RecipesBaseTestCase(BaseTestCase):
    '''Define assert method that every TestCase class will use'''
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create more users
        cls.auth_client_2 = APIClient()
        cls.user_authenticated_2 = UserModel.objects.create_user(
            username='auth_user_2', password='password',
            first_name='second_user', last_name='second_user',
            email='user2mail@gmail.com')
        token = Token.objects.create(user=cls.user_authenticated_2)
        cls.auth_client_2.credentials(
            HTTP_AUTHORIZATION='Token ' + token.key)

    def setUp(cls):
        # Create Tags isntances
        Tag.objects.bulk_create(
            [
                Tag(name='breakfast',
                    slug='breakfast'),
                Tag(name='dinner',
                    slug='dinner')
            ]
        )

        # Create Ingredients instances
        Ingredient.objects.bulk_create(
            [
                Ingredient(name='carrot',
                           measurement_unit='gramm'),
                Ingredient(name='potato',
                           measurement_unit='gramm')
            ]
        )

        # create Recipes instances
        Recipe.objects.bulk_create(
            [
                Recipe(author=cls.user_authenticated_1,
                       name='recipe1',
                       cooking_time=10,
                       short_link='qwerty1'
                       ),
                Recipe(author=cls.user_authenticated_2,
                       name='recipe2',
                       cooking_time=10,
                       short_link='qwerty2'
                       )
            ]
        )


class RecipeAPITestCase(RecipesBaseTestCase):
    '''
    Tests related to Recipes.
    '''
    BASE_URL = '/api/recipes'

    def setUp(cls):
        super().setUp()
        first_users_recipe_id = Recipe.objects.get(
            author=cls.user_authenticated_1
        ).id
        cls.existing_recipe_url = cls.BASE_URL + f'/{first_users_recipe_id}/'
        cls.non_existing_recipe_url = cls.BASE_URL + '/9999/'

    # Anonymous can get list of recipes page.
    def test_access_home_page(self):
        # Act
        url = reverse('api:recipes-list')
        response = self.client.get(url)

        # Assert
        self.assertEqual(
            response.status_code,
            200,
            "API did not return a 200 status code.")
        self.assertEqual(response.headers['Content-Type'],
                         'application/json',
                         "Response is not in JSON format.")

        json_data = response.json()

        self.assertIn('results', json_data,
                      "'results' key is not present in the response.")

        self.assertIsInstance(json_data['results'], list,
                              "'results' is not a list.")

    # Anonymous can access page of specific recipe.
    def test_access_a_recipe_view_page(self):
        # Act
        url = reverse('api:recipes-detail', args=[1])
        response = self.client.get(url)

        # Assert
        self.assertEqual(
            response.status_code,
            200,
            "API did not return a 200 status code.")
        self.assertEqual(response.headers['Content-Type'],
                         'application/json',
                         "Response is not in JSON format.")

    # Anonymous user can not make a recipe.
    def test_anonymous_cannot_make_a_recipe(self):
        url = reverse('api:recipes-list')
        payload = {
            "ingredients": [
                {
                    "id": 1,
                    "amount": 10
                },
            ],
            "tags": [
                1,
                2
            ],
            "image": "data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABA"
            "gMAAABieywaAAAACVBMVEUAAAD///9fX1/"
            "S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAA"
            "ACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "name": "should_not_be_created",
            "text": "string",
            "cooking_time": 1
        }
        response = self.client.post(
            url,
            payload,
            format='json')

        self.assertEqual(
            response.status_code,
            401,
            "API should return a 401 status code for unauthnticated user."
        )
        self.assertEqual(0,
                         len(Recipe.objects.filter(name='should_not_be_created'
                                                   )),
                         'Recipe should not be created.')

    # Authenticated user can create recipe via API endpoint
    def test_authenticated_user_can_create_recipe(self):
        url = reverse('api:recipes-list')
        payload = {
            "ingredients": [
                {
                    "id": 1,
                    "amount": 10
                }
            ],
            "tags": [
                1,
                2
            ],
            "image": "data:image/png;base64,iVBORw"
            "0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaA"
            "AAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7"
            "EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "name": "should_be_created",
            "text": "string",
            "cooking_time": 1
        }
        response = self.auth_client_1.post(
            url,
            payload,
            format='json')

        self.assertEqual(
            response.status_code,
            201,
            f"{(response.content)} \n"
            "API should return a 201 status code for authenticated user."
        )
        self.assertGreater(
            len(Recipe.objects.filter(name='should_be_created')),
            0,
            'Recipe should be created.')

    def test_recipe_updating(self):
        # Arrange
        correct_data = {
            "ingredients": [
                {
                    "id": 1,
                    "amount": 10
                }
            ],
            "tags": [
                1,
                2
            ],
            "image": "data:image/png;base64,iVBORw0"
            "KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAA"
            "AACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA"
            "7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "name": "New_name",
            "text": "new_string",
            "cooking_time": 100
        }
        incorrect_data = {
            "name": 'some nonsense'
        }
        test_cases = [
            (self.auth_client_1, 200, self.existing_recipe_url, correct_data,
             'User should be able to change his own recipe'),
            (self.auth_client_1, 400, self.existing_recipe_url, incorrect_data,
             'User should not be able to change his own recipe with wrong data'
             ),
            (self.client, 401, self.existing_recipe_url, correct_data,
             'Anonymous should not be able to change recipe'),
            (self.auth_client_2, 403, self.existing_recipe_url, correct_data,
             'User should not be able to change recipe of an another user'),
            (self.auth_client_1, 404, self.non_existing_recipe_url,
             correct_data,
             'User should not be able to change non existing recipe')
        ]
        # Act
        for client, expected_status, url, payload, error_msg in test_cases:
            with self.subTest(client=client,
                              expected_status=expected_status,
                              url=url, error_msg=error_msg
                              ):
                response = client.patch(url, payload, format='json')
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)

    def test_recipe_deleting(self):
        # Arrange
        test_cases = [
            (self.auth_client_2, 403, self.existing_recipe_url,
             'User should not be able to delete recipe of an another user'),
            (self.auth_client_1, 204, self.existing_recipe_url,
             'User should be able to delete his own recipe'),
            (self.client, 401, self.existing_recipe_url,
             'Anonymous should not be able to delete recipe'),
            (self.auth_client_1, 404, self.non_existing_recipe_url,
             'User should not be able to delete non existing recipe')
        ]
        # Act
        for client, expected_status, url, error_msg in test_cases:
            with self.subTest(client=client,
                              expected_status=expected_status,
                              url=url, error_msg=error_msg
                              ):
                response = client.delete(url)
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)

    def test_get_short_link(self):
        # Arrange
        existing_url = self.existing_recipe_url + 'get-link/'
        incorrect_url = self.non_existing_recipe_url + 'get-link/'
        test_cases = [
            (self.unauth_client, 200, existing_url,
             'Anonymous user should be able to receive short link'),
            (self.unauth_client, 404, incorrect_url,
             'Anonymous user should not be able to receive short link '
             'of non existing recipe')
        ]
        # Act
        for client, expected_status, url, error_msg in test_cases:
            with self.subTest(client=client,
                              expected_status=expected_status,
                              url=url, error_msg=error_msg
                              ):
                response = client.get(url)
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)
