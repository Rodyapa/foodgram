import shortuuid
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram.constants import (MAX_NAME, MAX_TAG_LENGTH, MAX_TEXT_DESCRIPTION,
                                MAX_UNIT_LENGTH)

from .validators import HexColorValidator

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
    color = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        validators=(HexColorValidator, ),
        default='#FFFFFF',
        db_index=False
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ("name",)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_NAME,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_UNIT_LENGTH
    )

    def __str__(self) -> str:
        return self.name


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
        validators=[MinValueValidator(1), MaxValueValidator(600)]
    )

    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )

    short_link = models.CharField(max_length=128, unique=True,
                                  default=shortuuid.ShortUUID().random())

    def save(self, *args, **kwargs):
        created = self.pk
        if created is None:
            random_string = shortuuid.ShortUUID().random()
            self.short_link = random_string
        super(Recipe, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "author"),
                name="unique_for_author",
            ),
        )

    def __str__(self) -> str:
        return self.name


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
        validators=(MaxValueValidator(10000), MinValueValidator(1)),
        verbose_name='Количество',
        default=1,
        blank=False
    )

    class Meta:
        verbose_name = "Количество ингридиента"
        verbose_name_plural = "Количество ингридиентов"
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='ingredient_recipe_unique')
        ]
        default_related_name = 'ingredient_recipes'

    def __str__(self) -> str:
        return f'Amount of  {self.ingredient.name} in the {self.recipe.name}'


class UserRelatedConditionOfRecipe(models.Model):

    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.recipe.name} of {self.user.username}'


class FavoriteRecipe(UserRelatedConditionOfRecipe):
    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_recipe_unique')
        ]


class ShopingCart(UserRelatedConditionOfRecipe):
    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="recipe_in_cart_already",
            ),
        )
