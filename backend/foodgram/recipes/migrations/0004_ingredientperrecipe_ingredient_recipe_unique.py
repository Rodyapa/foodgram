# Generated by Django 5.0.6 on 2024-06-10 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredientperrecipe_amount'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ingredientperrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='ingredient_recipe_unique'),
        ),
    ]
