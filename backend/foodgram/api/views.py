from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from recipes.models import (FavoriteRecipe, Ingredient, IngredientPerRecipe,
                            Recipe, ShopingCart, Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters as drf_filters
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import permissions as custom_permissions
from .filters import RecipeFilter
from .serializers import (AvatarResponseSerializer, AvatarSerializer,
                          CustomUserSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserRecipesSerializer)

User = get_user_model()


class CustomUserViewSet(djoser_views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated, ]
        return super().get_permissions()

    @action(detail=True, methods=['post', ],
            permission_classes=[permissions.IsAuthenticated, ],)
    def subscribe(self, request, id=None):
        request.data['user'] = request.user.id
        if not User.objects.filter(id=self.kwargs['id']).exists():
            return Response(data={
                'user': 'Вы пытаетесь подписатсья на несуществующего юзера',
            },
                status=status.HTTP_404_NOT_FOUND)
        request.data['target_user'] = self.kwargs['id']
        serializer = SubscriptionSerializer(data=request.data,
                                            context={"request": request}
                                            )
        if serializer.is_valid():
            serializer.save()
            target_user = User.objects.get(id=id)
            return_user = UserRecipesSerializer(target_user,
                                                context={"request": request})
            return Response(
                data=return_user.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', ],
            serializer_class=UserRecipesSerializer)  # THIS method excessive
    def recepies(self, request, id):
        user = self.get_object()
        related_recipes = Recipe.objects.filter(author=user)
        serializer = RecipeShortSerializer(related_recipes, many=True)
        if serializer.is_valid:
            return Response(serializer.data)
        return Response(serializer.errors)

    @action(methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated, ])
    def subscriptions(self, request):
        user = self.request.user
        subscribed_users = User.objects.filter(subscribers__user=user)
        serializer = UserRecipesSerializer(subscribed_users,
                                           context={"request": request},
                                           many=True)
        if serializer.is_valid:
            return Response(serializer.data)
        return Response(serializer.errors)

    @action(methods=['put', 'delete'], detail=False,
            permission_classes=[permissions.IsAuthenticated, ],
            url_path='me/avatar/')
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            if serializer.is_valid():
                request.user.avatar = serializer.validated_data['avatar']
                request.user.save()
                response = AvatarResponseSerializer(request.user)
                return Response(response.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(
                {'message': 'Avatar deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )


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

    permission_classes = [custom_permissions.IsAuthorOrIsStaffOrReadOnly, ]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.select_related("author")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            serializer_class=UserRecipesSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(
                    user=request.user,
                    recipe__id=pk).exists():
                return Response({
                    'errors': 'Рецепт уже добавлен в избранное'
                }, status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            obj = FavoriteRecipe.objects.filter(
                user=request.user,
                recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                'errors': 'Рецепт уже удален'
            }, status=status.HTTP_400_BAD_REQUEST)
        return None

    @action(detail=True, methods=['get'],
            url_path='get-link'
            )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        short_link = f"https://foodgram.example.org/s/{recipe.short_link}"
        return JsonResponse({"short-link": short_link})

    @action(detail=True, methods=['post', 'delete', ],
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            if ShopingCart.objects.filter(user=request.user,
                                          recipe__id=pk).exists():
                return Response({
                    'errors': 'Рецепт уже добавлен в корзину'
                }, status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, id=pk)
            ShopingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            obj = ShopingCart.objects.filter(
                user=request.user,
                recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                'errors': 'Рецепт уже удален'
            }, status=status.HTTP_400_BAD_REQUEST)
        return None

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients = IngredientPerRecipe.objects.filter(
            recipe__shopping_cart__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount')
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                final_list[name]['amount'] += item[2]
        pdfmetrics.registerFont(
            TTFont('Lato-Regular', 'Lato-Regular.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('Lato-Regular', size=18)
        page.drawString(200, 800, 'Список ингредиентов')
        page.setFont('Lato-Regular', size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(75, height, (f'{i}.  {name} - {data["amount"]}, '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response
