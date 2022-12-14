from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import SubscriptionsFilter
from .models import Subscription, User
from .serializers import SubscriptionGetSerializer, SubscriptionPostSerializer


class SubscriptionViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionGetSerializer
    filter_class = SubscriptionsFilter

    @action(
        detail=False,
        url_path='subscriptions',
    )
    def get_subscriptions(self, request):
        subscriptions_list = self.paginate_queryset(User.objects.filter(
            following__user=self.request.user))
        serializer = SubscriptionGetSerializer(
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
            serializer = SubscriptionPostSerializer(
                data={'user': self.request.user.id, 'author': author.id})
            if serializer.is_valid():
                serializer.save()
                subscriptions_serializer = SubscriptionGetSerializer(
                    author, context={'request': request})
                return Response(subscriptions_serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    'Данные не прошли валидацию',
                    status=status.HTTP_400_BAD_REQUEST)
        if change_subscription.exists():
            change_subscription.delete()
            return Response(f'Вы больше не подписаны на {author}',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(f'Вы не подписаны на {author}',
                        status=status.HTTP_400_BAD_REQUEST)
