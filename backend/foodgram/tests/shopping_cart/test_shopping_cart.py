
from recipes.models import Recipe, ShopingCart
from django.contrib.auth import get_user_model
from tests.base_test import BaseTestCase
from django.db import transaction

UserModel = get_user_model()


class DownloadShoppingCartTestCase(BaseTestCase):
    def test_download_shoppping_cart(self):
        # Arrange
        url = '/api/recipes/download_shopping_cart/'
        test_cases = [
            (self.auth_client_1, 200,
             'Response should be 200'),
            (self.client, 401,
             'Anonymous should not be able to download shopping cart')
        ]
        # Act
        for client, expected_status, error_msg in test_cases:
            with self.subTest(client=client,
                              expected_status=expected_status,
                              error_msg=error_msg):
                response = client.get(url)
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)


class RecipeAdditionToShoppingCart(BaseTestCase):
    def setUp(cls):
        cls.existing_recipe_url = '/api/recipes/1/shopping_cart/'
        cls.non_existing_recipe_url = '/api/recipes/9999/shopping_cart/'
        with transaction.atomic():
            cls.recipe = Recipe.objects.create(author=cls.user_authenticated_1,
                                               name='recipe1',
                                               cooking_time=10,
                                               short_link='qwerty1'
                                               )

    def test_recipe_addition_to_shopping_cart(self):
        # Arrange
        test_cases = [
            (self.auth_client_1, 201, self.existing_recipe_url,
             'User should be able to add recipe to the shopping cart'),
            (self.auth_client_1, 400, self.existing_recipe_url,
             'User should not be able to add recipe to the shopping cart twice'
             ),
            (self.client, 401, self.existing_recipe_url, 
             'Anonymous should not be able to add recipe to the shopping cart'
             ),
            (self.auth_client_1, 404, self.non_existing_recipe_url,
             'User should not be able to add non existing recipe to a card')
        ]
        # Act
        for client, expected_status, url, error_msg in test_cases:
            with self.subTest(client=client, expected_status=expected_status,
                              url=url, error_msg=error_msg):
                with transaction.atomic():
                    response = client.post(url)
                    # Assert
                    self.assertEqual(response.status_code, expected_status,
                                     error_msg)


class RecipeDeletionToShoppingCart(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.existing_recipe_url = '/api/recipes/1/shopping_cart/'
        cls.non_existing_recipe_url = '/api/recipes/9999/shopping_cart/'
        cls.recipe = Recipe.objects.create(author=cls.user_authenticated_1,
                                           name='recipe1',
                                           cooking_time=10,
                                           short_link='qwerty1'
                                           )
        cls.shopping_cart = ShopingCart(
            recipe=cls.recipe,
            user=cls.user_authenticated_1).save()

    def test_recipe_deleting_from_the_shopping_cart(self):
        # Arrange
        test_cases = [
            (self.auth_client_1, 204, self.existing_recipe_url,
             'User should be able to delete recipe from the shopping cart'),
            (self.auth_client_1, 404, self.existing_recipe_url,
             'User should not be able to delete recipe from '
             'the shopping cart twice'
             ),
            (self.client, 401, self.existing_recipe_url,
             'Anonymous should not be able to delete '
             'recipe from the shopping cart'
             ),
            (self.auth_client_1, 404, self.non_existing_recipe_url,
             'User should not be able to delete non existing '
             'recipe from a card')
        ]
        # Act
        for client, expected_status, url, error_msg in test_cases:
            with self.subTest(client=client, expected_status=expected_status,
                              url=url, error_msg=error_msg):
                response = client.delete(url)
                # Assert
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)
