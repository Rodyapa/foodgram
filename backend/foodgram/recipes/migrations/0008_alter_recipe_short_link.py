# Generated by Django 5.0.6 on 2024-06-13 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_recipe_short_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(default='nCxewFjRJaVez6Ynj7WjNB', max_length=128, unique=True),
        ),
    ]
