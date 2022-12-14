from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import SubscriptionViewSet
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register("users", SubscriptionViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
