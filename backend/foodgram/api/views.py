from djoser import views as djoser_views
from .serializers import (CustomUserSerializer,
                          CustomUserListSerializer,
                          AvatarSerializer,
                          SubscriptionSerializer,
                          TagSerializer,
                          IngredientSerializer)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from users.models import Subscription
from recipes.models import Tag, Ingredient
from rest_framework import authentication, permissions
from djoser import permissions as djoser_permissions
from rest_framework import viewsets, generics, mixins, status, views
from rest_framework.response import Response
User = get_user_model()


class CustomUserViewSet(djoser_views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_serializer_class(self, *args, **kwargs):
        if self.action == "list":
            return CustomUserListSerializer
        return super().get_serializer_class(*args, **kwargs)
    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated,]
        return super().get_permissions()


class AvatarView(views.APIView):
    permission_classes = [djoser_permissions.CurrentUserOrAdminOrReadOnly]
    def put(self, request):
        serializer = AvatarSerializer(data=request.data)
        if serializer.is_valid():
            request.user.avatar = serializer.validated_data['avatar']
            request.user.save()
            return Response({'message': 'Avatar updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request):
        request.user.avatar.delete()
        return Response({'message': 'Avatar deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class SubscriptionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated,]
    def get(self, request):
        pass
    def post(self, request):
        user = self.request.user
        target_user = get_object_or_404(user_id=self.kwargs['target_id'])
        data = {"user": user, "target_user": target_user}
        serializer = SubscriptionSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            Subscription.objects.create(serializer.data)
        

class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer