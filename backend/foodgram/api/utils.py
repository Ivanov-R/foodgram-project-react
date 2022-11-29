from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredient
from users.serializers import RecipeShortSerializer


def create_or_update_recipeingredients(ingredients, recipe):
    objs = []
    for ingredient in ingredients:
        objs.append(RecipeIngredient(
            recipe=recipe, ingredient=ingredient['id'],
            amount=ingredient['amount'],))
    RecipeIngredient.objects.bulk_create(objs)


def add_to_or_delete_from_it(
        request, pk, picked_serializer, model, field):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'POST':
        data = {}
        data['user'] = request.user.id
        data[field] = recipe.id
        serializer = picked_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            new_serializer = RecipeShortSerializer(recipe)
            return Response(new_serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(
                'Данные не прошли валидацию',
                status=status.HTTP_400_BAD_REQUEST)
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
