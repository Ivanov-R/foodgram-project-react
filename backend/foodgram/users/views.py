from django.shortcuts import get_object_or_404, render
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping_cart, Tag)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
# from .permissions import OwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, ShoppingCartListSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (OwnerOrReadOnly,)

    # @action(
    #     detail=False,
    #     url_path='shopping_cart',
    # )
    # def add_to_shopping_cart(self, request, pk):
    #     """Позволяет текущему пользователю добавлять рецепты
    #     в список покупок"""
    #     recipe = get_object_or_404(Recipe, pk=pk)
    #     if request.method == 'POST':
    #         serializer = ShoppingCartSerializer(
    #             data={'user': request.user.id, 'shopping_recipe': recipe.id})
    #         serializer.is_valid()
    #         serializer.save()
    #         shopping_cart_serializer = RecipeShortSerializer(recipe)
    #         return Response(shopping_cart_serializer.data,
    #                         status=status.HTTP_201_CREATED)
    #     shopping_cart_recipe = get_object_or_404(
    #         Shopping_cart, user=request.user, shopping_recipe=recipe
    #     )
    #     shopping_cart_recipe.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
