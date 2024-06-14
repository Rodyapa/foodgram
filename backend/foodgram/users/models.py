from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator
from django.db import models

from foodgram.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH


class CustomUser(AbstractUser):
    """
    Измененная стандартная модель пользователя Django.
    """

    class Roles(models.TextChoices):
        ADMIN = 'admin'
        REGULAR = 'regular'

    username = models.CharField(
        verbose_name='Уникалный username',
        max_length=MAX_USERNAME_LENGTH,
        validators=[UnicodeUsernameValidator(),
                    ],
        unique=True,
        blank=False
    )
    email = models.EmailField(
        verbose_name='Email пользователя',
        max_length=MAX_EMAIL_LENGTH,
        validators=[EmailValidator, ],
        unique=True,

    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=16,
        choices=Roles.choices,
        default=Roles.REGULAR,
    )
    first_name = models.CharField(
        "Имя пользователя",
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        "Фамилия пользователя",
        max_length=150,
        blank=False
    )
    avatar = models.ImageField(
        verbose_name='Аватар пользователя',
        upload_to='user_avatars/',
        blank=True
    )

    REQUIRED_FIELDS = ["username", "last_name", "first_name"]
    USERNAME_FIELD = "email"

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN

    @property
    def is_regular(self):
        return self.role == self.Roles.REGULAR

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """
    Подписки пользователя.
    """
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=CustomUser,
        on_delete=models.CASCADE,
        blank=False,
        related_name='subscriptions'
    )
    target_user = models.ForeignKey(
        verbose_name='Подписки',
        to=CustomUser,
        on_delete=models.CASCADE,
        blank=False,
        related_name='subscribers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'target_user'],
                                    name='user_target_user_unique',)
        ]
