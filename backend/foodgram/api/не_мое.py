from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                           ShoppingCart, Tag)
from users.models import Follow, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        write_only_fields = ('password',)
        read_only_fields = ('id',)
        extra_kwargs = {'is_subscribed': {'required': False}}

    def get_is_subscribed(self, author):
        """Получение статуса подписки.
        Определеяет подписан ли пользователь
        на просматриваемого пользователя"""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        else:
            return Follow.objects.filter(
                user=user,
                author=author,
            ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор краткого отображения рецепта"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок"""

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        """Статус подписки"""
        request = self.context.get('request')
        if not request:
            return True
        return (
            Follow.objects.filter(
                user=request.user,
                author__id=obj.author.id
            ).exists()
            and request.user.is_authenticated
        )

    def get_recipes_count(self, obj):
        """Получение количества рецептов"""
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes,
            many=True
        ).data


class FollowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = (
            'user',
            'author',
        )
        read_only_fields = (
            'user',
            'author',
        )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        sub_id = self.context['request'].parser_context['kwargs']['user_id']
        author = get_object_or_404(
            User,
            id=sub_id
        )
        user = self.context['request'].user
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        if Follow.objects.filter(
                user=user,
                author=author
        ).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на {author}.'
            )
        return data

    def create(self, validated_data):
        author = get_object_or_404(
            User,
            id=self.context['request'].parser_context['kwargs']['user_id']
        )
        Follow.objects.create(
            user=self.context['request'].user,
            author=author
        )
        return author


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class ShowIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор вывода ингредиентов рецепта"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    # id = serializers.ReadOnlyField(source='ingredient.id')
    # name = serializers.ReadOnlyField(source='ingredient.name')
    # amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            # 'name',
            'amount',
        )


class ShowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецепта"""

    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'is_favorite',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_in_shopping_cart',
        )

    def get_is_favorite(self, obj):
        """Статус наличия в избранном"""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Статус наличия в списке покупок"""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ShowIngredientsInRecipeSerializer(ingredients, many=True).data


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта"""

    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(
        use_url=True,
        max_length=None,
    )
    name = serializers.CharField(max_length=254)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
        )

    def validate_tags(self, tags):
        """Валидация тегов"""
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Необходимо заполнить тег'
            })
        tags_set = set()
        for tag in tags:
            tags_set.add(tag)
        return tags_set

    def validate_ingredients(self, ingredients):
        """Валидация ингредиентов"""
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты необходимо заполнить'
            })
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients:
                raise serializers.ValidationError(
                    {
                        'ingredients': f'{ingredient} существует, измените'
                    })
            amount = ingredient['amount']
            if int(amount) < 1:
                raise serializers.ValidationError({
                    'amount': 'Количество должно быть больше 0'
                })
            return ingredients

    def validate_cooking_time(self, cooking_time):
        """Валидация времени приготовления"""
        if int(cooking_time) < 1 or cooking_time is None:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 0'
            })
        return cooking_time

    def add_ingredients(self, ingredients, recipe):
        """Добавление ингредиентов"""
        for ingredient in ingredients:
            ingr, _ = RecipeIngredient.objects.get_or_create(
                # Рецепт обязательное поле
                # recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            recipe.ingredients.add(ingr)

    def add_tags(self, tags, recipe):
        """Добавление тегов"""
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        """Создание рецепта"""
        # author = self.context.get('request').user
        # tags = validated_data.pop('tags')
        # ingredients = validated_data.pop('ingredients')
        # image = validated_data.pop('image')
        # recipe, _ = Recipe.objects.get_or_create(
        #     image=image, **validated_data
        # )
        # self.add_tags(tags, recipe)
        # self.add_ingredients(ingredients, recipe)
        # return recipe
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        """Обновление рецепта"""
        recipe.tags.clear()
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.add_tags(validated_data.pop('tags'), recipe)
        self.add_ingredients(validated_data.pop('ingredients'))
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        """Функция отображения рецепта"""
        return ShowRecipeSerializer(
            recipe,
            context=self.context,
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного"""

    user = serializers.HiddenField(
        default=CustomUserSerializer(read_only=True)
    )
    recipe = ShortRecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=(
                    'user',
                    'recipe',
                ),
                message='Рецепт уже в избранном',
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок"""

    user = serializers.HiddenField(
        default=CustomUserSerializer(read_only=True)
    )
    recipe = ShortRecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=(
                    'user',
                    'recipe',
                ),
                message="Рецепт уже в списке покупок",
            )
        ]
