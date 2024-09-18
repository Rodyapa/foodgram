from django.test import TestCase
from recipes.models import Ingredient


class GetIngredientTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Ingredient.objects.bulk_create(
            [
                Ingredient(name='carrot',
                           measurement_unit='gramm'),
                Ingredient(name='potato',
                           measurement_unit='gramm')
            ]
        )

    def test_get_ingredient_list(self):
        # Arrange
        url = '/api/ingredients/'
        # Act
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200,
                         'Anonymous should be able to get ingredients list.')
        self.assertEqual(response.headers['Content-Type'],
                         'application/json',
                         "Response is not in JSON format.")

    def test_get_specific_ingredient(self):
        # Arrange
        exisitng_tag_url = '/api/ingredients/1/'
        non_existing_tag_url = '/api/ingredients/9999/'
        test_cases = [
            (exisitng_tag_url, 200,
             'User should be able to receive specific ingredient'),
            (non_existing_tag_url, 404,
             'User should receive 404 error if ingredient doesnt exist')
        ]
        # Act
        for url, expected_status, error_msg in test_cases:
            with self.subTest(url=url, expected_status=expected_status,
                              error_msg=error_msg):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status,
                                 error_msg)
                if expected_status == 200:
                    self.assertEqual(
                        response.headers['Content-Type'],
                        'application/json',
                        "Response is not in JSON format.")
