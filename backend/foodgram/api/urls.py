from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet,
                    AvatarView,
                    SubscriptionView,
                    TagViewSet,
                    IngredientViewSet)

api_v1 = DefaultRouter()
api_v1.register(r'users', CustomUserViewSet, basename='users')
api_v1.register(r'tags', TagViewSet, basename='tags')
api_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
api_v1_urlpatterns = {
    path(
        route=r'users/me/avatar/',
        view=AvatarView.as_view(),
        name='avatar-view'),
    path(
        route='users/<int:target_id>/subscribe',
        view=SubscriptionView.as_view(),
        name='subscription-view')
}
urlpatterns = [
    path('', include(api_v1.urls)),
    path('', include(api_v1_urlpatterns)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
