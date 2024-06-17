from django.contrib.admin import ModelAdmin, register, site
from recipes.models import Ingredient, Recipe
from users.models import CustomUser

site.site_header = "Foodgram администрирование"


@register(CustomUser)
class UserAdmin(ModelAdmin):
    search_fields = ("first_name", "username", "email")
    list_filter = ("first_name", "username", "email")


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        "name",
        "author",
        "count_favorites"
    )
    fields = (
        (
            "name",
            "cooking_time",
        ),
        (
            "author",
            "tags",
        ),
        ("text",)
    )
    raw_id_fields = ("author",)
    search_fields = (
        "name",
        "author__username",
        "tags__name",
    )
    list_filter = ("name", "author__username", "tags__name")

    def count_favorites(self, obj):
        return obj.favoriterecipe_set.count()

    count_favorites.short_description = "В избранном"


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
