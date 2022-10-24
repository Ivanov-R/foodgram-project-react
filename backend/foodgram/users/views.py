from api.pagination import CustomPagination
from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping_cart, Tag)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscription, User
# from .permissions import OwnerOrReadOnly
from .serializers import RecipeShortSerializer, SubscriptionSerializer


class SubscriptionViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer

    @action(
        detail=False,
        url_path='subscriptions',
    )
    def get_subscriptions(self, request):
        recipes_limit = int(request.query_params['recipes_limit'])
        if recipes_limit:
            authors = User.objects.filter(following__user=self.request.user)
            subscriptions_list = self.paginate_queryset(
                authors[0].recipes.all()[:recipes_limit])

        else:
            subscriptions_list = self.paginate_queryset(User.objects.filter(
                follower=self.request.user))
        serializer = RecipeShortSerializer(
            subscriptions_list, many=True, context={
                'request': request
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        change_subscription = Subscription.objects.filter(
            user=user.id, author=author.id
        )
        if request.method == 'POST':
            if user == author:
                return Response('Нельзя подписаться на себя!',
                                status=status.HTTP_400_BAD_REQUEST)
            if change_subscription.exists():
                return Response(f'Вы уже подписаны на {author}',
                                status=status.HTTP_400_BAD_REQUEST)
            subscribe = Subscription.objects.create(
                user=user,
                author=author
            )
            subscribe.save()
            return Response(f'Вы подписались на {author}',
                            status=status.HTTP_201_CREATED)
        if change_subscription.exists():
            change_subscription.delete()
            return Response(f'Вы больше не подписаны на {author}',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(f'Вы не подписаны на {author}',
                        status=status.HTTP_400_BAD_REQUEST)
