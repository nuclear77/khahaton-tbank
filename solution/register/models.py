from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    daily_calories = models.IntegerField(default=2000)
    # Используем строковую ссылку вместо прямого импорта
    liked_dishes = models.ManyToManyField('app.Dish', blank=True)

    def __str__(self):
        return self.user.username


# Сигналы для автоматического создания профиля
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()