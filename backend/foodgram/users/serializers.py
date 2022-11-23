from djoser.serializers import UserSerializer
from recipes.models import Recipe
from rest_framework import serializers

from .models import Subscription, User


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, value):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=value).exists()


class UserCreateSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')


class SubscriptionGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes')

    def get_is_subscribed(self, value):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=value).exists()


class SubscriptionPostSerializer(UserSerializer):

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')
