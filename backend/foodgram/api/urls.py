from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, AvatarView

api_v1 = DefaultRouter()
api_v1.register(r'users', CustomUserViewSet, basename='users')
api_v1_urlpatterns = {
    path(route=r'users/me/avatar/', view=AvatarView.as_view(), name='avatar-view')
}
urlpatterns = [
    path('', include(api_v1.urls)),
    path('', include(api_v1_urlpatterns)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
