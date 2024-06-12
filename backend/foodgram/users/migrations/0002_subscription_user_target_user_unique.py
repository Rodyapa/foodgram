# Generated by Django 5.0.6 on 2024-06-12 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'target_user'), name='user_target_user_unique'),
        ),
    ]
