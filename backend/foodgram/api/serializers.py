from djoser.serializers import UserCreateSerializer, UserSerializer
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

    class Meta:
        model = Favorite
        fields = ('user', 'favorite_recipe')
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


# class UserCreateSerializer(UserCreateSerializer):

#     class Meta:
#         fields = ('email', 'id', 'username', 'first_name', 'last_name')


# class UserCreateSerializer(UserCreateSerializer):

#     class Meta:
#         fields = ('email', 'id', 'username', 'first_name', 'last_name')

class RecipesReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_list",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_user(self):
        return self.context["request"].user

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()
