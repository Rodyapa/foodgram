from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from djoser import serializers as djoser_serialisers
from recipes.models import Ingredient, IngredientPerRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from users.models import Subscription
from users.validators import CantSubscribeMyselfValdiator, username_validator
from .fields import Base64ImageField
from foodgram.constants import MAX_USERNAME_LENGTH

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer,
                           djoser_serialisers.UserCreateMixin):

    username = serializers.CharField(
        validators=[MaxLengthValidator(MAX_USERNAME_LENGTH),
                    username_validator,
                    UniqueValidator(queryset=User.objects.all())
                    ],
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
            "password",
        )
        read_only_fields = ["id", ]

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        request_user = self.context['request'].user
        if request_user == obj:
            return False
        else:
            subscribed = Subscription.objects.filter(user=request_user,
                                                     target_user=obj)
            if subscribed:
                return True
        return False


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class AvatarResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['avatar']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientPerRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientPerRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount', ]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientPerRecipeSerializer(source='ingredient_recipes',
                                                many=True,
                                                read_only=True,)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  "is_in_shopping_cart",
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                  ]

    def validate(self, data):
        tags = self.initial_data.get("tags")
        tag_ids_list = []
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Должен быть хотя бы один тег'}
            )
        for tag_id in tags:
            tag = Tag.objects.filter(id=tag_id)
            if not tag.exists():
                raise serializers.ValidationError({
                    'tags': 'Указан не существующий тег'})
            if tag_id in tag_ids_list:
                raise serializers.ValidationError('Теги не должны повторяться')
            tag_ids_list.append(tag_id)
        ingredients = self.initial_data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients':
                'Нужно добавить хотя бы один ингридиент для рецепта'})
        ingredient_ids_list = []
        for ingredient_item in ingredients:
            ingredient = Ingredient.objects.filter(id=ingredient_item['id'])
            if not ingredient.exists():
                raise serializers.ValidationError({
                    'ingredients':
                    'Указан не существующий ингридиент'})
            if ingredient_item['id'] in ingredient_ids_list:
                raise serializers.ValidationError('Ингридиенты должны '
                                                  'быть уникальными')
            ingredient_ids_list.append(ingredient_item['id'])
            if int(ingredient_item['amount']) <= 0:
                raise serializers.ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента в рецепте больше 0')
                })
        author = self.context["request"].user
        data.update(
            {
                "tags": tags,
                "ingredients": ingredients,
                "author": author,
            }
        )
        return data

    def get_is_favorited(self, recipe: Recipe):
        user = self.context['request'].user

        if not user.is_authenticated:
            return False
        in_favourite = user.favorites.filter(recipe=recipe).exists()
        return in_favourite

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        is_in_shopping_cart = user.shopping_cart.filter(recipe=recipe).exists()
        return is_in_shopping_cart

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            recipe.tags.add(tag)
        for ingredient_item in ingredients_data:
            ingredient, amount = ingredient_item.values()
            recipe.ingredients.add(
                ingredient,
                through_defaults={'amount': amount}
            )
        return recipe

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'tags':
                instance.tags.set(value)
            elif attr == 'ingredients':
                instance.ingredients.clear()
                objs = []
                for ingredient_data in value:
                    ingredient_id, amount = ingredient_data.values()
                    ingredient_instance = Ingredient.objects.get(
                        id=ingredient_id
                    )
                    objs.append(
                        IngredientPerRecipe(
                            recipe=instance,
                            ingredient=ingredient_instance,
                            amount=amount
                        ))
                IngredientPerRecipe.objects.bulk_create(objs)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            "user",
            "target_user"
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'target_user'],
                message='Вы уже подписаны на этого пользователя'
            ),
            CantSubscribeMyselfValdiator()

        ]


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id',
                  'name',
                  'image',
                  'cooking_time'
                  ]
        read_only_fields = ['id',
                            'name',
                            'image',
                            'cooking_time'
                            ]


class UserRecipesSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
    )
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
            "recipes_count",
            "recipes"
        )

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        request_user = self.context['request'].user
        if request_user == obj:
            return False
        else:
            subscribed = Subscription.objects.filter(user=request_user,
                                                     target_user=obj)
            if subscribed:
                return True
        return False

    def get_recipes_count(self, obj):
        recipes_count = obj.recipes.count()
        return recipes_count

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.id)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeShortSerializer(queryset, many=True).data
