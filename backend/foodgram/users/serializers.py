from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscription, User
from users.utils import subscribe


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name",
                  "last_name", "is_subscribed")

    def get_is_subscribed(self, value):
        request = self.context.get("request")
        user = request.user
        result = subscribe(user, value)
        return result


class UserCreateSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class SubscriptionGetSerializer(UserGetSerializer):
    recipes = RecipeShortSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
        )


class SubscriptionPostSerializer(UserSerializer):
    class Meta:
        model = Subscription
        fields = ("id", "user", "author")

    def validate_author(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Такого автора не существует")
        return value
