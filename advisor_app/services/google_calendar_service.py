# smart_advisor_project/advisor_app/services/google_calendar_service.py

from django.conf import settings
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build, HttpError
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials # Ensure this is the Credentials object you're using
import datetime
import logging

logger = logging.getLogger(__name__)

def get_google_auth_flow():
    """
    Initializes and returns the Google OAuth flow object.
    Raises ValueError if OAuth settings are incomplete.
    """
    if not all([settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET, settings.GOOGLE_REDIRECT_URI]):
        msg = "Google OAuth settings (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI) are not fully configured."
        logger.critical(msg)
        raise ValueError(msg)

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "project_id": settings.GOOGLE_PROJECT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
        }
    }
    try:
        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=settings.GOOGLE_CALENDAR_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        return flow
    except Exception as e:
        logger.error(f"Error creating Google OAuth Flow: {e}")
        raise ValueError(f"Could not initialize Google OAuth Flow: {e}")


def get_calendar_events(credentials: Credentials):
    """
    Fetches upcoming events from Google Calendar using provided credentials.
    Handles token refresh if necessary.
    Returns a dictionary like {"events": [...], "refreshed_credentials": Credentials_object_if_refreshed_else_None}
    or {"error": "message", "needs_reauth": True/False}.
    """
    if not credentials:
        logger.warning("get_calendar_events called with no credentials.")
        return {"error": "Google credentials not provided.", "needs_reauth": True}

    was_refreshed = False # Flag to track if a refresh occurred in this call

    if not credentials.valid: # .valid property checks expiry and other validity aspects
        if credentials.expired and credentials.refresh_token:
            try:
                logger.info("Google token expired or invalid, attempting refresh.")
                # Store token before refresh to compare later if needed, though not strictly necessary for this fix
                # original_token = credentials.token 
                credentials.refresh(GoogleAuthRequest())
                was_refreshed = True # Mark that a refresh happened
                logger.info("Google token refreshed successfully within get_calendar_events.")
            except Exception as e: # Includes google.auth.exceptions.RefreshError
                logger.error(f"Failed to refresh Google token within get_calendar_events: {e}")
                return {"error": f"Could not refresh Google token. Please re-authenticate. ({e})", "needs_reauth": True}
        else:
            logger.warning("Google credentials invalid and no refresh token, or not expired but still invalid.")
            return {"error": "Google credentials invalid. Please re-authenticate.", "needs_reauth": True}

    try:
        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        now_utc = datetime.datetime.utcnow().isoformat() + 'Z'

        logger.debug(f"Fetching Google Calendar events from: {now_utc}")
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now_utc,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        logger.info(f"Successfully fetched {len(events)} Google Calendar events.")
        
        # If a refresh occurred during this function call, return the updated credentials object
        # The .valid property is the main check for usability.
        return {
            "events": events,
            "refreshed_credentials": credentials if was_refreshed else None
        }

    except HttpError as e:
        logger.error(f"Google Calendar API HttpError: {e.status_code} - {e._get_reason()}")
        if e.resp.status == 401:
            return {"error": "Google Calendar access denied (401). Please re-authenticate.", "needs_reauth": True}
        return {"error": f"An error occurred with Google Calendar API: {e._get_reason()}", "needs_reauth": False}
    except AttributeError as ae: # Catch specific AttributeError if it occurs elsewhere
        logger.error(f"AttributeError during Google Calendar API call: {ae}", exc_info=True)
        return {"error": f"A configuration or object error occurred with Google Calendar: {ae}", "needs_reauth": False}
    except Exception as e:
        logger.error(f"Unexpected error fetching Google Calendar events: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred with Google Calendar: {e}", "needs_reauth": False}