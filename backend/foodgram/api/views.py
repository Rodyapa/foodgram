from djoser import views as djoser_views
from .serializers import CustomUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserViewSet(djoser_views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
