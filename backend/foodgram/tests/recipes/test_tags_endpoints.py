from django.test import TestCase
from recipes.models import Tag


class GetTagTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Tag.objects.bulk_create(
            [
                Tag(name='breakfast',
                    slug='breakfast'),
                Tag(name='dinner',
                    slug='dinner')
            ]
        )

    def test_get_tag_list(self):
        # Arrange
        url = '/api/tags/'
        # Act
        response = self.client.get(url)
        # Assert
        self.assertEqual(response.status_code, 200,
                         'Anonymous should be able to get tag list.')
        self.assertEqual(response.headers['Content-Type'],
                         'application/json',
                         "Response is not in JSON format.")

    def test_get_specific_tag(self):
        # Arrange
        exisitng_tag_url = '/api/tags/1/'
        non_existing_tag_url = '/api/tags/9999/'
        test_cases = [
            (exisitng_tag_url, 200,
             'User should be able to receive specific tag'),
            (non_existing_tag_url, 404,
             'User should receive 404 error if tag doesnt exist')
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
