# Generated by Django 5.0.6 on 2024-06-18 03:30

import recipes.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0018_alter_recipe_short_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(default='RpmbmiFbfE7L5CRT2UT7xs', max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(default='#FFFFFF', max_length=7, validators=[recipes.validators.HexColorValidator], verbose_name='Цвет'),
        ),
    ]
