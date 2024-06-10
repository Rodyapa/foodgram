from rest_framework import serializers
from djoser import serializers as djoser_serialisers
from foodgram.constants import MAX_USERNAME_LENGTH
from users.validators import username_validator
from django.core.validators import MaxLengthValidator
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from users.models import Subscription
from recipes.models import Tag, Ingredient, Recipe
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import base64
import uuid
User = get_user_model()

class CustomUserCreateSerialzier(djoser_serialisers.UserCreateSerializer):
    username = serializers.CharField(
        validators=[MaxLengthValidator(MAX_USERNAME_LENGTH),
                    username_validator,
                    UniqueValidator(queryset=User.objects.all())
        ],
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password"
        )


class CustomUserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        validators=[MaxLengthValidator(MAX_USERNAME_LENGTH),
                    username_validator,
                    UniqueValidator(queryset=User.objects.all())
        ],
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
        )


class CustomUserListSerializer(CustomUserSerializer):
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        )


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


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = (
            "user",
            "target_user"
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        field = '__all__'