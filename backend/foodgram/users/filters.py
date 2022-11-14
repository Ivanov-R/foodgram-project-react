from django_filters import rest_framework as filter
from recipes.models import Recipe


class SubscriptionsFilter(filter.FilterSet):
    recipes_limit = filter.NumberFilter(
        field_name='recipes_limit',
        method='get_recipes_limit',
    )

    def get_recipes_limit(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            queryset = queryset.filter(
                following__user__user=self.request.user).values('recipes')[
                : int(value)]
            return queryset
        return queryset

    class Meta:
        model = Recipe
        fields = ['recipes_limit', ]
