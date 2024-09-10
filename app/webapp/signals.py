from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def promote_new_user_to_superuser(sender, instance, created, **kwargs):
    if created:
        # Automatically promote the new user to superuser
        instance.is_superuser = True
        instance.is_staff = True  # Required for admin access
        instance.save()
