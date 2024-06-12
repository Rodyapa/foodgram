from rest_framework import serializers
from djoser import serializers as djoser_serialisers
from foodgram.constants import MAX_USERNAME_LENGTH
from users.validators import username_validator, CantSubscribeMyselfValdiator
from django.core.validators import MaxLengthValidator
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from users.models import Subscription
from recipes.models import Tag, Ingredient, Recipe, IngredientPerRecipe
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import base64
import uuid
User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):

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
            "avatar",
            "password",
            "is_subscribed"
        )
    
    def get_is_subscribed(self, obj):
        request_user = self.context['request'].user
        if request_user == obj:
            return False
        else:
            subscribed = Subscription.objects.filter(user=request_user,
                                                     target_user=obj)
            if subscribed:
                return True
        return False


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


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
        fields = ['id', 'name', 'measurement_unit', 'amount',]



class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientPerRecipeSerializer(source='ingredient_recipes',
                                                many=True,
                                                read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                  ]


class IngredientPerRecipeCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientPerRecipe
        fields = ['id', 'amount',]


class RecipeCreateUpdateSerialzier(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientPerRecipeCreateUpdateSerializer(
        source='ingredient_recipes',
        many=True,
        )

    image = Base64ImageField()
    class Meta:
        model = Recipe
        fields = ['id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                  ]
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name'],
                message='Пользователь не может иметь рецепты с одинаковыми названиями'
            ),]


    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredient_recipes')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            recipe.tags.add(tag)
        for ingredient in ingredients_data:
            ingredient, amount = ingredient.values()
            recipe.ingredients.add(ingredient['id'], through_defaults={'amount':amount})
        return recipe

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'tags':
                instance.tags.clear()
                for tag in value:
                    instance.tags.add(tag)
            elif attr == 'ingredient_recipes':
                instance.ingredients.clear()
                for ingredient in value:
                    ingredient, amount = ingredient.values()
                    instance.ingredients.add(
                        ingredient['id'],
                        through_defaults={'amount': amount}
                    )
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

class RecipeInlineSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)

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
    recipes = RecipeInlineSerializer( many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "recipes"
        )
