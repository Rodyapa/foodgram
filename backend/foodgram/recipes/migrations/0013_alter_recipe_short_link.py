# Generated by Django 5.0.6 on 2024-06-18 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_tag_color_alter_favoriterecipe_recipe_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(default='WKDZ4AiKYGfVVC6NRQx3yJ', max_length=128, unique=True),
        ),
    ]
