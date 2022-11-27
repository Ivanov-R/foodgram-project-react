from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from recipes.models import Recipe, RecipeIngredient
from rest_framework import status
from rest_framework.response import Response
from users.serializers import RecipeShortSerializer


def create_or_update_recipeingredients(ingredients, recipe):
    objs = []
    try:
        for ingredient in ingredients:
            objs.append(RecipeIngredient(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount'],))
        RecipeIngredient.objects.bulk_create(objs)
    except IntegrityError:
        raise IntegrityError("Ингредиенты или тэги дублируются")


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
