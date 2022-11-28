from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.serializers import UserGetSerializer
from .utils import create_or_update_recipeingredients


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True, read_only=True, source='ingredients_recipes')
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
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_user(self):
        return self.context["request"].user

    def get_is_favorited(self, obj):
        user = self.get_user()
        if user.is_anonymous:
            return False
        return user.favorites.filter(favorite_recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(shopping_recipe=obj).exists()


class RecipePostPatchSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        queryset=Tag.objects.all(),
        required=True,
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientPostSerializer(many=True, required=True)
    image = Base64ImageField()
    name = serializers.CharField()
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_tags(self, value):
        for tag in value:
            if not Tag.objects.filter(name=tag).exists():
                raise serializers.ValidationError("Такого тэга не существует")
        tags_set = set(value)
        if len(value) != len(tags_set):
            raise serializers.ValidationError("Тэги не должны дублироваться")
        return value

    def validate_ingredients(self, value):
        for ingredient in value:
            if not Ingredient.objects.filter(name=ingredient).exists():
                raise serializers.ValidationError(
                    "Такого ингредиента не существует")
        ingredients_set = set(value)
        if len(value) != len(ingredients_set):
            raise serializers.ValidationError(
                "Ингредиенты не должны дублироваться")
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_or_update_recipeingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        create_or_update_recipeingredients(ingredients, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        return RecipeGetSerializer(
            recipe,
            context=self.context,
        ).data


class RecipeDestroySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = Recipe
        fields = (
            "id",
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'shopping_recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=(
                    'user',
                    'shopping_recipe',
                ),
                message="Рецепт уже входит в список покупок",
            )
        ]

    def validate_shopping_recipe(self, value):
        if not Recipe.objects.filter(name=value).exists():
            raise serializers.ValidationError("Такого рецепта не существует")
        return value


class ShoppingCartListSerializer(serializers.ModelSerializer):
    shopping_cart = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('shopping_cart')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'favorite_recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "favorite_recipe"))]

    def validate_favorite_recipe(self, value):
        if not Recipe.objects.filter(name=value).exists():
            raise serializers.ValidationError("Такого рецепта не существует")
        return value
