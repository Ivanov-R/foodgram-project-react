from djoser.serializers import UserSerializer
from recipes.models import Recipe
from rest_framework import serializers

from .models import Subscription, User
from .utils import subscribe


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
        user = request.user
        result = subscribe(user, value)
        return result


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
        user = request.user
        result = subscribe(user, value)
        return result


class SubscriptionPostSerializer(UserSerializer):

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')

    def validate_author(self, value):
        authors = list(User.objects.values_list('email'))
        result = list(map(lambda x: x[0], authors))
        if str(value) not in result:
            raise serializers.ValidationError("Такого автора не существует")
        return value
