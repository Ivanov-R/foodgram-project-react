from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping_cart, Tag)
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

# from .permissions import OwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class CreateListViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = (OwnerOrReadOnly,)
    # pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    # permission_classes = (OwnerOrReadOnly,)

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get("recipe_id"))
        new_queryset = Recipe.objects.filter(recipe=recipe)
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user, shopping_recipe=self.kwargs.get(
                "recipe_id"))
