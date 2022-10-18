from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping_cart, Tag)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    ingredients = serializers.StringRelatedField(
        many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'cooking_time',
                  'author', 'tags', 'ingredients')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shopping_cart
        fields = ('user', 'shopping_recipe')


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartListSerializer(serializers.ModelSerializer):
    shopping_cart = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Shopping_cart
        fields = ('shopping_cart')


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    favorite_recipe = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = ("user", "favorite_recipe")
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "favorite_recipe"))]

    # def validate(self, data):
    #     if data["favorite_recipe"].user == self.context["request"].user:
    #         raise serializers.ValidationError(
    #             "Нельзя подписываться на самого себя."
    #         )
    #     return data
