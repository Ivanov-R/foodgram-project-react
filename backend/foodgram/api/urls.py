from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCartViewSet, TagViewSet)

router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
# router.register(
#     r"recipes/(?P<recipe_id>[^/.]+)/shopping_cart",
#     ShoppingCartViewSet,
#     basename="shopping_cart",
# )
router.register(
    r"recipes/(?P<recipe_id>[^/.]+)/favorite",
    FavoriteViewSet,
    basename="favorite",
)

urlpatterns = [
    path("", include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]
