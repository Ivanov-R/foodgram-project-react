from django_filters import rest_framework as filter
from recipes.models import Recipe, Tag


class RecipeFilter(filter.FilterSet):
    tags = filter.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        label='Tags',
        to_field_name='slug'
    )
    is_favorited = filter.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filter.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited', 'is_in_shopping_cart', 'author']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not int(value) or user.is_anonymous:
            return queryset
        return queryset.filter(favorite_recipes__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart_recipes__user=user)
        return queryset
