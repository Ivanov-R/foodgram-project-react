from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping_cart, Tag)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from .models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    ingredients = serializers.StringRelatedField(
        many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'cooking_time',
                  'author', 'tags', 'ingredients')


class UserSubscribedSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'author', 'user')

    def get_is_subscribed(self, value):
        request = self.context.get('request')
        return Subscription.objects.filter(
            user=request.user, follower=value).exists()
