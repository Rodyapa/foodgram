import csv
import os
from django.core.files import File
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


def user_import(row):
    if not User.objects.filter(username=row[0]):
        User.objects.create_user(
            username=row[0],
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            password=row[4]
        )


def ingredients_import(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1]
    )


def tags_import(row):
    Tag.objects.get_or_create(
        name=row[0],
        slug=row[1]
    )


def recipes_import(row):
    # Get the image path from the row
    image_path = row[1]
    recipe = Recipe.objects.get_or_create(
        name=row[0],
        text=row[2],
        author_id=row[3],
        cooking_time=row[4],
    )[0]
    tags = list(row[5].split(","))
    ingredients = list(row[6].split(","))
    # Handle the image file
    if image_path:
        # Open the image file
        with open(os.path.join('../filling_data/filling_media/', image_path),
                  'rb') as img_file:
            # Save the image to the recipe instance
            recipe.image.save(os.path.basename(image_path), File(img_file))

    # Process tags and ingredients
    for tag in tags:
        recipe.tags.add(tag)
    for ingredient in ingredients:
        recipe.ingredients.add(ingredient)


def recipes_ingredients(row):
    pass


action = {
    'users.csv': user_import,
    'ingredients.csv': ingredients_import,
    'tags.csv': tags_import,
    'recipes.csv': recipes_import
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, '../filling_data/')
        for key in action.keys():
            with open(path + key, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    action[key](row)
