# Generated by Django 5.0.6 on 2024-06-18 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_alter_recipe_short_link_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(default='wj9K6XXngtm7WQNpCRTBnP', max_length=128, unique=True),
        ),
    ]
