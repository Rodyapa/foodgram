import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Tag, Recipe, Ingredient


def ingredients_import(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1]
    )


action = {
    'ingredients.csv': ingredients_import,
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, '../../data/')
        for key in action.keys():
            with open(path + key, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)
                for row in reader:
                    action[key](row)