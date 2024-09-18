from django.db import transaction
from recipes.models import FavoriteRecipe, Recipe
from tests.base_test import BaseTestCase


class FavouriteRecipeTestCase(BaseTestCase):    
    def setUp(self):
        self.recipe = Recipe.objects.create(author=self.user_authenticated_1,
                                            name='recipe1',
                                            cooking_time=10,
                                            short_link='qwerty1')
        self.existing_recipe_url = f'/api/recipes/{self.recipe.id}/favorite/'
        self.non_existing_recipe_url = '/api/recipe/9999/favorite/'

    def test_add_recipe_to_favorites(self):
        # Arrange
        test_cases = [
            (self.auth_client_1, 201, self.existing_recipe_url,
             'User should be able to add recipe to favorites.'),
            (self.auth_client_1, 400, self.existing_recipe_url,
             'User should not be able to add recipe to favorites twice.'),
            (self.client, 401, self.existing_recipe_url,
             'Anonymous should not be able to add recipe to favorites.'),
            (self.auth_client_1, 404, self.non_existing_recipe_url,
             'Attempt to add non-existing recipe to favorites must return 404')
        ]

        # Act
        for client, expected_status, url, error_msg in test_cases:
            with self.subTest(client=client, url=url,
                              expected_status=expected_status,
                              error_msg=error_msg):
                with transaction.atomic():
                    response = client.post(url)
                    # Assert
                    self.assertEqual(response.status_code, expected_status,
                                     error_msg)

    def test_delete_recipe_from_favorites(self):
        # Arrange
        FavoriteRecipe.objects.create(recipe=self.recipe,
                                      user=self.user_authenticated_1)

        test_cases = [
            (self.auth_client_1, 204, self.existing_recipe_url,
             'User should be able to delete recipe from favorites.'),
            (self.auth_client_1, 404, self.existing_recipe_url,
             'User should not be able to delete recipe from favorites twice.'),
            (self.client, 401, self.existing_recipe_url,
             'Anonymous should not be able to delete recipe from favorites.'),
            (self.auth_client_1, 404, self.non_existing_recipe_url,
             'Attempt to delete non-existing recipe '
             'from favorites must return 404')
        ]

        # Act
        for client, expected_status, url, error_msg in test_cases:
            with self.subTest(client=client, url=url, error_msg=error_msg, 
                              expected_status=expected_status):
                with transaction.atomic():
                    response = client.delete(url)
                    # Assert
                    self.assertEqual(response.status_code, expected_status,
                                     error_msg)