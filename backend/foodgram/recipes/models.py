from django.db import models
from slugify import slugify
from foodgram.constants import MAX_TEXT_DESCRIPTION, MAX_TAG_LENGTH, MAX_NAME, MAX_UNIT_LENGTH
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
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


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_NAME,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_UNIT_LENGTH
    )


class Recipe(models.Model):
    """Модель рецептов блюд."""

    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        to=User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='recipes'
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
    ingredients = models.ManyToManyField(
        verbose_name='Соотвествующие ингредиенты',
        blank=False,
        through="IngredientPerRecipe",
        through_fields=['recipe', 'ingredient'],
        to=Ingredient
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'name'],
                                    name='author_name_unique',
                                    )
        ]

class IngredientPerRecipe(models.Model):
    ingredient = models.ForeignKey(
        to=Ingredient,
        verbose_name='Название ингредиента',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MaxValueValidator(10000),),
        verbose_name='Количество',
        default=1,
        blank=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'], name='ingredient_recipe_unique')
        ]
        default_related_name = 'ingredient_recipes'
