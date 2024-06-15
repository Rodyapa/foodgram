from django.contrib.admin import (ModelAdmin, register, site)
from django.utils.safestring import SafeString, mark_safe
from recipes.models import (Ingredient, Recipe)
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
        "get_image",
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
        ("text",),
        ("image",),
        (
            "count_favorites",
        )
    )
    raw_id_fields = ("author",)
    search_fields = (
        "name",
        "author__username",
        "tags__name",
    )
    list_filter = ("name", "author__username", "tags__name")

    def get_image(self, obj: Recipe) -> SafeString:
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    get_image.short_description = "Изображение"

    def count_favorites(self, obj):
        return obj.in_favorites.count()

    count_favorites.short_description = "В избранном"


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
