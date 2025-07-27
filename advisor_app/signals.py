from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile
import logging

logger = logging.getLogger(__name__) # advisor_app.signals

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a UserProfile when a User instance is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"UserProfile created for new user: {instance.username}")
    else:
        # Ensure profile exists for existing users, perhaps created before this signal
        try:
            instance.profile.save() # Trigger save on existing profile if needed
            # logger.debug(f"UserProfile updated for existing user: {instance.username}")
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance) # Create if it somehow doesn't exist
            logger.warning(f"UserProfile was missing for existing user {instance.username} and has been created.")
        except Exception as e:
            logger.error(f"Error saving profile for user {instance.username} in signal: {e}")