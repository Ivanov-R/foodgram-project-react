from django.db.models import Sum
from django.http import HttpResponse
from django_filters import rest_framework as filter
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import filters, viewsets
from rest_framework.decorators import action

from .filters import RecipeFilter
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeDestroySerializer, RecipeGetSerializer,
                          RecipePostPatchSerializer, ShoppingCartSerializer,
                          TagSerializer)
from .utils import add_to_or_delete_from_it


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (filter.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeGetSerializer
        if self.action == 'retrieve':
            return RecipeGetSerializer
        if self.action == 'destroy':
            return RecipeDestroySerializer
        return RecipePostPatchSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
    )
    def add_to_shopping_cart_or_delete_from_it(self, request, pk):
        shopping_recipe = 'shopping_recipe'
        result = add_to_or_delete_from_it(
            request, pk, ShoppingCartSerializer, ShoppingCart,
            shopping_recipe)
        return result

    @action(
        detail=False,
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = 'Cписок покупок:'
        shopping_cart = RecipeIngredient.objects.filter(
            recipe__in=Recipe.objects.filter(shopping_cart_recipes__user=user))
        shopping_cart = shopping_cart.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(
            amount_sum=Sum('amount'))
        for num, i in enumerate(shopping_cart):
            ingredients += (
                f"\n{i['ingredient__name']} - "
                f"{i['amount_sum']} {i['ingredient__measurement_unit']}"
            )
            if num < shopping_cart.count() - 1:
                ingredients += ', '
        file = 'shopping_list'
        response = HttpResponse(
            ingredients, 'Content-Type: application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
    )
    def add_to_favorite_or_delete_from_it(self, request, pk):
        favorite_recipe = 'favorite_recipe'
        result = add_to_or_delete_from_it(
            request, pk, FavoriteSerializer, Favorite, favorite_recipe)
        return result
