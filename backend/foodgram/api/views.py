from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping_cart, Tag)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from users.serializers import RecipeShortSerializer

# from .permissions import OwnerOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeDestroySerializer, RecipeGetSerializer,
                          RecipeIngredientGetSerializer,
                          RecipePostPatchSerializer, ShoppingCartSerializer,
                          TagSerializer)


class CreateDeleteListViewSet(
        mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
        viewsets.GenericViewSet):
    pass


class CreateDeleteViewSet(
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    pass


# class RecipeFilter(filters.FilterSet):
#     min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
#     max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')

#     class Meta:
#         model = Recipe
#         fields = ['author__id', 'tags']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # permission_classes = (OwnerOrReadOnly,)
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = [RecipeFilter]

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
    def add_to_shopping_cart(self, request, pk):
        """Позволяет текущему пользователю добавлять рецепты
        в список покупок"""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'shopping_recipe': recipe.id})
            serializer.is_valid()
            serializer.save()
            shopping_cart_serializer = RecipeShortSerializer(recipe)
            return Response(shopping_cart_serializer.data,
                            status=status.HTTP_201_CREATED)
        shopping_cart_recipe = get_object_or_404(
            Shopping_cart, user=request.user, shopping_recipe=recipe
        )
        shopping_cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     detail=False,
    #     url_path='download_shopping_cart',
    # )
    # def download_shopping_cart(self, request):
    #     user = self.request.user
    #     ingredients = 'Cписок покупок:'
    #     shopping_cart = user.shopping_cart.values(
    #         'ingredient__name', 'ingredient__measurement_unit'
    #     ).annotate(amount=sum('amount'))
    #     for num, i in enumerate(shopping_cart):
    #         ingredients += (
    #             f"\n{i['ingredient__name']} - "
    #             f"{i['amount']} {i['ingredient__measurement_unit']}"
    #         )
    #         if num < shopping_cart.count() - 1:
    #             ingredients += ', '
    #     file = 'shopping_list'
    #     response = HttpResponse(
    #         ingredients, 'Content-Type: application/pdf'
    #     )
    #     response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    #     return response
        # print(shopping_cart)
        # for recipe in shopping_cart:

        #     # serializer = RecipeIngredientGetSerializer(shopping_cart, many=True)
        # return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
    )
    def add_to_favorite(self, request, pk):
        """Позволяет текущему пользователю добавлять рецепты
        в избранное"""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'favorite_recipe': recipe.id})
            serializer.is_valid()
            serializer.save()
            favorite_serializer = RecipeShortSerializer(recipe)
            return Response(favorite_serializer.data,
                            status=status.HTTP_201_CREATED)
        fav_recipe = get_object_or_404(
            Favorite, user=request.user, favorite_recipe=recipe
        )
        fav_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDeleteListViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = Shopping_cart.objects.all()
    # permission_classes = (OwnerOrReadOnly,)
    pagination_class = None

    # def get_queryset(self):
    #     recipe = get_object_or_404(Recipe, pk=self.kwargs.get("recipe_id"))
    #     new_queryset = Recipe.objects.filter(recipe=recipe)
    #     return new_queryset

    # def perform_create(self, serializer):
    #     serializer.save(
    #         user=self.request.user, shopping_recipe_id=self.kwargs.get(
    #             "recipe_id"))

    # def get_serializer_class(self):
    #     if self.action == 'list':
    #         return ShoppingCartListSerializer
    #     return ShoppingCartSerializer

    # @action(detail=False, url_path='download_shopping_cart')
    # def download_shopping_cart(self, request):
    #     shopping_cart = Shopping_cart.objects.filter(user=self.request.user)
    #     serializer = self.get_serializer(shopping_cart, many=True)
    #     return Response(serializer.data)


class FavoriteViewSet(CreateDeleteViewSet):
    serializer_class = FavoriteSerializer
    # permission_classes = (OwnerOrReadOnly,)
    pagination_class = None

    def get_queryset(self):
        favorite_recipe = get_object_or_404(
            Recipe, pk=self.kwargs.get("recipe_id"))
        new_queryset = Favorite.objects.filter(favorite_recipe=favorite_recipe)
        # new_queryset = self.request.user.user_favorite.all()
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        favorite_recipe=Recipe.objects.get(
                            id=self.kwargs.get("recipe_id")))
