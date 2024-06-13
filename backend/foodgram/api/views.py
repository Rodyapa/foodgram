from djoser import views as djoser_views
from .serializers import (CustomUserSerializer,
                          AvatarSerializer,
                          SubscriptionSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          UserRecipesSerializer,
                          RecipeShortSerializer,
                          AvatarResponseSerializer,
                          )
from .filters import RecipeFilter
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from users.models import Subscription
from recipes.models import Tag, Ingredient, Recipe, FavoriteRecipe
from rest_framework import authentication, permissions
from . import permissions as custom_permissions
from djoser import permissions as djoser_permissions
from rest_framework import viewsets, generics, mixins, status, views
from rest_framework import filters as  drf_filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import SAFE_METHODS
from django.http import JsonResponse
User = get_user_model()


class CustomUserViewSet(djoser_views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated,]
        return super().get_permissions()

    @action(detail=True, methods=['post',],
            permission_classes=[permissions.IsAuthenticated,],)
    def subscribe(self, request, id=None):
        request.data['user'] = request.user.id
        request.data['target_user'] = self.kwargs['id']
        serializer = SubscriptionSerializer(data=request.data,)
        if serializer.is_valid():
            serializer.save()
            target_user = User.objects.get(id=id)
            return_user = CustomUserSerializer(target_user)
            return Response(data=return_user.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get',],
            serializer_class=UserRecipesSerializer) # THIS method doesn't required by docs. CAn b Deleted
    def recepies(self, request, id):
        user = self.get_object()
        related_recipes = Recipe.objects.filter(author=user)
        serializer = RecipeShortSerializer(related_recipes, many=True)
        if serializer.is_valid:
            return Response(serializer.data)
        return Response(serializer.errors)

    @action(detail=True, methods=['get'],
            serializer_class=UserRecipesSerializer)
    def subscriptions(self, request, id):
        user = self.request.user
        subscribed_users = User.objects.filter(subscribers__user=user)
        serializer = UserRecipesSerializer(subscribed_users, many=True)
        if serializer.is_valid:
            return Response(serializer.data)
        return Response(serializer.errors)

class AvatarView(views.APIView):
    permission_classes = [djoser_permissions.CurrentUserOrAdminOrReadOnly]
    def put(self, request):
        serializer = AvatarSerializer(data=request.data)
        if serializer.is_valid():
            request.user.avatar = serializer.validated_data['avatar']
            request.user.save()
            response = AvatarResponseSerializer(request.user)
            return Response(response.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request):
        request.user.avatar.delete()
        return Response({'message': 'Avatar deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    
    permission_classes = [custom_permissions.IsAuthorOrIsStaffOrReadOnly,]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.select_related("author")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'],
            serializer_class=UserRecipesSerializer,
            permission_classes=[permissions.IsAuthenticated])    
    def favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        favorite_recipe, created = FavoriteRecipe.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if not created:
            return Response(
                'Вы уже добавили этот рецепт в избранное',
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite_recipe_serialized = RecipeShortSerializer(
            data=favorite_recipe
        )
        return Response(favorite_recipe_serialized,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'],
            url_path='get-link'
            )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        short_link = f"https://foodgram.example.org/s/{recipe.short_link}"
        return JsonResponse({"short-link": short_link})