from .models import Subscription


def subscribe(user, author):
    if user.is_anonymous:
        return False
    return Subscription.objects.filter(
        user=user, author=author).exists()
