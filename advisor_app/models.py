# smart_advisor_project/advisor_app/models.py

from django.db import models
from django.contrib.auth.models import User
import json
import logging
import datetime

logger = logging.getLogger(__name__)

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Enter a City (e.g., Mumbai, London) or a specific address. Country-level searches (e.g., 'India') may not yield Eventbrite results."
    )
    google_credentials_json = models.TextField(
        blank=True,
        null=True,
        help_text="Stores Google OAuth credentials as JSON. Handle with care."
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def set_google_credentials(self, credentials):
        if hasattr(credentials, 'to_json'):
            try:
                self.google_credentials_json = credentials.to_json()
                logger.debug(f"Successfully serialized and set Google credentials for user {self.user.username}")
            except Exception as e:
                logger.error(f"Error during credentials.to_json() for user {self.user.username}: {e}")
                self.google_credentials_json = None
        else:
            logger.error(
                f"Attempted to set Google credentials for {self.user.username} "
                f"with an object of type '{type(credentials).__name__}' which lacks a 'to_json' method."
            )
            self.google_credentials_json = None
        self.save()

    def get_google_credentials(self):
        if not self.google_credentials_json:
            logger.debug(f"No Google credentials JSON found for user {self.user.username}")
            return None
        try:
            from google.oauth2.credentials import Credentials
            creds_info_dict = json.loads(self.google_credentials_json)
            if 'expiry' in creds_info_dict and isinstance(creds_info_dict['expiry'], str):
                expiry_str_value = creds_info_dict['expiry']
                logger.debug(f"Found string expiry '{expiry_str_value}' for user {self.user.username}. Attempting to parse to naive UTC.")
                try:
                    parsed_datetime_aware = None
                    if expiry_str_value.endswith('Z'):
                        if '.' in expiry_str_value: dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"
                        else: dt_format = "%Y-%m-%dT%H:%M:%SZ"
                        parsed_datetime_aware = datetime.datetime.strptime(expiry_str_value, dt_format).replace(tzinfo=datetime.timezone.utc)
                    else:
                        parsed_datetime_aware = datetime.datetime.fromisoformat(expiry_str_value)
                    if parsed_datetime_aware:
                        datetime_in_utc_aware = parsed_datetime_aware.astimezone(datetime.timezone.utc)
                        creds_info_dict['expiry'] = datetime_in_utc_aware.replace(tzinfo=None)
                        logger.info(f"Successfully parsed expiry string to NAIVE UTC datetime for user {self.user.username}: {creds_info_dict['expiry']}")
                    else: logger.warning(f"Could not create an aware datetime from expiry string '{expiry_str_value}' for user {self.user.username}.")
                except ValueError as ve: logger.error(f"ValueError parsing expiry string '{expiry_str_value}' for user {self.user.username}: {ve}.")
            credentials = Credentials(**creds_info_dict)
            logger.debug(f"Successfully retrieved and constructed Google credentials object for user {self.user.username}")
            return credentials
        except json.JSONDecodeError as e: logger.error(f"JSONDecodeError loading Google credentials for {self.user.username}. Data (first 100 chars): '{self.google_credentials_json[:100] if self.google_credentials_json else 'None'}'. Error: {e}")
        except TypeError as e:
            dict_keys = list(creds_info_dict.keys()) if 'creds_info_dict' in locals() else "Unknown"
            logger.error(f"TypeError creating Credentials object for {self.user.username}. Dict keys: {dict_keys}. Error: {e}")
        except Exception as e: logger.error(f"Unexpected error loading Google credentials for {self.user.username}: {e}", exc_info=True)
        return None

    @property
    def has_valid_google_credentials(self):
        creds = self.get_google_credentials()
        return creds and creds.valid