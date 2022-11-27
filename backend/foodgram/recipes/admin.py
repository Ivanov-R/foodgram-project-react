from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_filter = [
        "name",
        "author",
        "tags"
    ]
    list_display = ('name', 'author', 'favorite_count')

    def favorite_count(self, obj):
        return obj.favorite_recipes.count()


class IngredientAdmin(admin.ModelAdmin):
    list_filter = [
        "name"
    ]
    list_display = ('name', 'measurement_unit')


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
