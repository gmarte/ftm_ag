from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    class Role(models.TextChoices):
        PARENT = 'PARENT', 'Parent'
        KID = 'KID', 'Kid'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PARENT)
    points = models.IntegerField(default=0)
    # Allows linking a kid to a parent (simple hierarchy)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='kids')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
