import requests
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import Recipe, Ingredient, Tag
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

UserModel = get_user_model()


class AuthenticatedTestCase(TestCase):
    '''Define assert method that every TestCase class will use'''
    @classmethod
    def setUpTestData(cls):
        # Create Users
        cls.auth_client_1 = APIClient()
        cls.auth_client_2 = APIClient()

        cls.user_authencticated_1 = UserModel.objects.create_user(
            username='auth_user_1', password='password',
            first_name='first_user', last_name='first_user',
            email='user1mail@gmail.com')

        cls.user_authencticated_2 = UserModel.objects.create_user(
            username='auth_user_2', password='password',
            first_name='second_user', last_name='second_user',
            email='user2mail@gmail.com')

        # Get token
        response = cls.auth_client_1.post('/api/auth/token/login', {
            'email': 'user1mail@gmail.com', 'password': 'password'})
        token = response.data['auth_token']

        # Set token for all test cases
        cls.auth_client_1.credentials(HTTP_AUTHORIZATION=f'Token {token}')

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

        #Create Recipes instances
        Recipe.objects.bulk_create(
            [
                Recipe(author=cls.user_authencticated_1,
                       name='recipe1',
                       cooking_time=10,
                       short_link='qwerty1'
                       ),
                Recipe(author=cls.user_authencticated_2,
                       name='recipe2',
                       cooking_time=10,
                       short_link='qwerty2'
                       )
            ]
        )


class RecipeAPITestCase(AuthenticatedTestCase):
    '''
    Tests related to Recipes.
    '''

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
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
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
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
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

    # Anonymous can not access delete and edit pages of recipe.
    def test_cannot_access_recipe_delete_page(self):
        pass
        # Act

    def test_cannot_access_recipe_edit_page(self):
        pass

    # Anonymous can get log in, log out and sign in pages.
    def test_authentication_and_authorization_pages(self):
        pass
    # Anonymous can access static info pages.
    def test_access_info_pages(self):
        pass


class AuthenticatedUserTestCase(TestCase):
    '''
    Tests checks that authenticated user can access 
    edit and delete pages of his/her recipes.
    '''
    # Author of recipe can access delete or edit recipe pages.
    def test_access_delete_page(self):
        pass

    def test_acess_edit_page(self):
        pass
    # Logged user can not access delete or edit pages someone else's recipes.

    def test_cannot_access_anothers_edit_recipe_page(self):
        pass

    def test_cannot_access_anothers_delete_recipe_page(self):
        pass