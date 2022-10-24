from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping_cart, Tag)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from users.serializers import UserGetSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        ingredient = RecipeIngredient.objects.get(ingredient=obj)
        return ingredient.amount


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(validators=[MinValueValidator(1)])
    id = serializers.IntegerField(source='ingredient_id')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    # def get_ingredient(self):
    #     ingredient = RecipeIngredient.objects.get(ingredient=id)
    #     return ingredient


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = RecipeIngredientGetSerializer(many=True)
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
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.favorites.filter(favorite_recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
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

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        print(ingredients_data)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            print(ingredient)
            ingredient, _ = RecipeIngredient.objects.get_or_create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount'],)
            print(ingredient)
            recipe.ingredients.add(ingredient)
        return recipe


class RecipeDestroySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = Recipe
        fields = (
            "id",
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shopping_cart
        fields = ('user', 'shopping_recipe')


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
