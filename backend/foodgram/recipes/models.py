from django.db import models
from slugify import slugify
from foodgram.constants import MAX_TEXT_DESCRIPTION, MAX_TAG_LENGTH
from django.contrib.auth import get_user_model
User = get_user_model()


class Tag(models.Model):
    """Модель текстовых тегов для рецептов."""

    name = models.CharField(
        verbose_name='Название тега',
        max_length=MAX_TAG_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='уникальное название тега',
        unique=True
    )


class Recipe(models.Model):
    """Модель рецептов блюд."""

    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        to=User,
        on_delete=models.CASCADE,
        blank=False,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=128,
        blank=False
    )
    image = models.ImageField(
        verbose_name="Картинка рецепта",
        upload_to='recipes_images/',
        blank=True
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        max_length=MAX_TEXT_DESCRIPTION
    )
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name='Соответствующие теги',
        blank=True
    )
    cooking_time = models.TimeField(
        verbose_name='Время приготовления',
    )