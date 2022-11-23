from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filter
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping_cart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.serializers import RecipeShortSerializer

from .filters import RecipeFilter
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeDestroySerializer, RecipeGetSerializer,
                          RecipePostPatchSerializer, ShoppingCartSerializer,
                          TagSerializer)


def add_to_or_delete_from_it(
        request, pk, picked_serializer, model, field):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'POST':
        data = {}
        data['user'] = request.user.id
        data[field] = recipe.id
        serializer = picked_serializer(data=data)
        serializer.is_valid()
        serializer.save()
        new_serializer = RecipeShortSerializer(recipe)
        return Response(new_serializer.data,
                        status=status.HTTP_201_CREATED)
    if field == 'shopping_recipe':
        recipe_unit = get_object_or_404(
            model, user=request.user, shopping_recipe=recipe
        )
    else:
        recipe_unit = get_object_or_404(
            model, user=request.user, favorite_recipe=recipe
        )
    recipe_unit.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


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
            request, pk, ShoppingCartSerializer, Shopping_cart,
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
