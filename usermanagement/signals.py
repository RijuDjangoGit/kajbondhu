# myapp/signals.py
from django.db.models import Avg
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import UserRating, UserProfile


def _recalculate_and_store_average(user):
    """
    Compute the new average for all ratings belonging to `user`
    and persist it on that user’s profile (to 2 decimals).
    """
    average = (
        UserRating.objects.filter(user=user)
        .aggregate(avg=Avg("rating"))["avg"] or 0
    )
    # round to 2 decimals so it fits max_digits=3, decimal_places=2
    average = round(average, 2)

    # update only the rating column for efficiency
    UserProfile.objects.filter(user=user).update(rating=average)


@receiver(post_save, sender=UserRating)
def update_rating_on_save(sender, instance, **kwargs):
    _recalculate_and_store_average(instance.user)


@receiver(post_delete, sender=UserRating)
def update_rating_on_delete(sender, instance, **kwargs):
    _recalculate_and_store_average(instance.user)
