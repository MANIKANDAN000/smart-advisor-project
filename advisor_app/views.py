# smart_advisor_project/advisor_app/views.py

import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.http import HttpRequest, HttpResponse

from .models import UserProfile
from .services import weather_service, google_calendar_service, eventbrite_service

from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
import logging

logger = logging.getLogger(__name__)

if settings.DEBUG:
    if 'OAUTHLIB_INSECURE_TRANSPORT' not in os.environ:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        logger.warning("Setting OAUTHLIB_INSECURE_TRANSPORT=1 in code for development...")
    elif os.environ['OAUTHLIB_INSECURE_TRANSPORT'] != '1':
        logger.warning(f"OAUTHLIB_INSECURE_TRANSPORT is '{os.environ['OAUTHLIB_INSECURE_TRANSPORT']}', expected '1' for local HTTP dev.")

@login_required
def home_view(request: HttpRequest) -> HttpResponse:
    user_profile = request.user.profile
    context = {
        'user_profile': user_profile,
        'weather_data': None,
        'calendar_data': {"events": None, "error": None, "needs_reauth": False},
        'eventbrite_data': {"events": None, "error": None}, # Initialize to handle potential errors
        'google_auth_url': None,
    }

    # Fetch Weather Data
    if user_profile.location:
        logger.debug(f"Fetching weather for user {request.user.username}, location: {user_profile.location}")
        context['weather_data'] = weather_service.get_weather_data(user_profile.location)
        if context['weather_data'].get('error'):
            logger.warning(f"Weather service error for {request.user.username}: {context['weather_data']['error']}")
    else:
        logger.info(f"User {request.user.username} has no location set for weather.")

    # Fetch Eventbrite Data
    if user_profile.location:
        logger.debug(f"Fetching Eventbrite events for user {request.user.username}, location: {user_profile.location}")
        # The value of user_profile.location is passed to the service.
        # If this is "India", the service will call Eventbrite with location.address=India.
        context['eventbrite_data'] = eventbrite_service.get_eventbrite_events(location_address=user_profile.location)
        if context['eventbrite_data'].get('error'):
            logger.warning(f"Eventbrite service error for {request.user.username}: {context['eventbrite_data']['error']}")
            # Optionally, add a Django message to show the user (template needs to display it)
            # messages.warning(request, f"Eventbrite: {context['eventbrite_data']['error']}")
    else:
        logger.info(f"User {request.user.username} has no location set for Eventbrite.")

    # Handle Google Calendar
    google_credentials = user_profile.get_google_credentials()
    if not google_credentials or not google_credentials.valid:
        if google_credentials and google_credentials.expired and google_credentials.refresh_token:
            try:
                logger.info(f"Attempting to refresh Google token for user {request.user.username}")
                from google.auth.transport.requests import Request as GoogleAuthRequest
                google_credentials.refresh(GoogleAuthRequest())
                user_profile.set_google_credentials(google_credentials)
                logger.info(f"Google token refreshed for {request.user.username}.")
                messages.info(request, "Google session refreshed.")
            except RefreshError as e:
                logger.error(f"Google token refresh failed for {request.user.username}: {e}. Forcing re-auth.")
                messages.error(request, "Your Google session has expired and could not be refreshed. Please connect again.")
                user_profile.google_credentials_json = None
                user_profile.save()
                google_credentials = None
            except Exception as e:
                logger.error(f"Unexpected error during Google token refresh for {request.user.username}: {e}")
                messages.error(request, "An unexpected error occurred with your Google session. Please connect again.")
                user_profile.google_credentials_json = None
                user_profile.save()
                google_credentials = None
        else:
            if google_credentials: messages.warning(request, "Your Google connection needs to be re-established.")
            google_credentials = None

    if google_credentials and google_credentials.valid:
        logger.debug(f"Fetching Google Calendar events for {request.user.username}")
        calendar_api_result = google_calendar_service.get_calendar_events(google_credentials)
        context['calendar_data'].update(calendar_api_result)
        if calendar_api_result.get('error') and not calendar_api_result.get('needs_reauth'):
            messages.warning(request, f"Google Calendar: {calendar_api_result['error']}")
        if calendar_api_result.get('refreshed_credentials'):
            logger.info("Credentials were refreshed by the calendar service. Re-saving.")
            user_profile.set_google_credentials(calendar_api_result['refreshed_credentials'])
    else:
        try: context['google_auth_url'] = reverse('google_calendar_init')
        except Exception as e:
            logger.error(f"Could not reverse 'google_calendar_init': {e}")
            messages.error(request, "Error setting up Google Calendar connection link.")

    return render(request, 'advisor_app/home.html', context)

# ... (profile_view and Google OAuth views remain the same as previous robust versions) ...

@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    user_profile = request.user.profile
    if request.method == 'POST':
        location = request.POST.get('location', '').strip()
        if location:
            user_profile.location = location
            user_profile.save()
            logger.info(f"User {request.user.username} updated location to: {location}")
            messages.success(request, 'Location updated successfully!')
        else:
            logger.warning(f"User {request.user.username} attempted to set an empty location.")
            messages.error(request, 'Location cannot be empty.')
        return redirect('profile')
    return render(request, 'advisor_app/profile.html', {'user_profile': user_profile})

@login_required
def google_calendar_init_view(request: HttpRequest) -> HttpResponse:
    try:
        flow = google_calendar_service.get_google_auth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline', prompt='consent', include_granted_scopes='true'
        )
        request.session['oauth_state'] = state
        logger.info(f"Google OAuth: Initiating flow for {request.user.username}. State: {state}")
        return redirect(authorization_url)
    except ValueError as e:
        logger.critical(f"Google OAuth configuration error during init: {e}")
        messages.error(request, "Google Calendar integration is not configured correctly by the site administrator.")
        return redirect('home')
    except Exception as e:
        logger.error(f"Unexpected error initiating Google OAuth flow for {request.user.username}: {e}")
        messages.error(request, "Could not start Google Calendar connection. Please try again.")
        return redirect('home')

@login_required
def google_calendar_oauth2callback_view(request: HttpRequest) -> HttpResponse:
    state_from_session = request.session.pop('oauth_state', None)
    state_from_google = request.GET.get('state')
    if not state_from_session or state_from_session != state_from_google:
        logger.error(f"OAuth state mismatch for user {request.user.username}. Session: '{state_from_session}', Google: '{state_from_google}'")
        messages.error(request, "Authentication failed due to a state mismatch. Please try connecting again.")
        return redirect('home')
    if 'error' in request.GET:
        error = request.GET.get('error')
        logger.warning(f"Google OAuth callback error for user {request.user.username}: {error}")
        messages.error(request, f"Google declined the connection: {error}. Please try again.")
        return redirect('home')
    try:
        flow = google_calendar_service.get_google_auth_flow()
        flow.fetch_token(authorization_response=request.build_absolute_uri())
    except ValueError as e:
        logger.critical(f"Google OAuth configuration error on callback: {e}")
        messages.error(request, "Google Calendar integration is not configured correctly (callback).")
        return redirect('home')
    except Exception as e:
        logger.error(f"Failed to fetch Google OAuth token for {request.user.username}: {e}. URL: {request.build_absolute_uri()}", exc_info=True)
        error_message = str(e)
        if "MismatchingRedirectURIError" in error_message: messages.error(request, "OAuth Redirect URI mismatch. Check Google Cloud Console and Django settings.")
        elif "insecure_transport" in error_message.lower(): messages.error(request, "OAuth connection failed due to insecure transport. Check server logs.")
        else: messages.error(request, f"Failed to finalize Google Calendar connection: {e}. Ensure cookies are enabled and try again.")
        return redirect('home')
    if not flow.credentials:
        logger.error(f"Google OAuth flow completed but no credentials obtained for {request.user.username}.")
        messages.error(request, "Could not obtain Google credentials after authentication. Please try again.")
        return redirect('home')
    user_profile = request.user.profile
    user_profile.set_google_credentials(flow.credentials)
    logger.info(f"Google Calendar successfully connected for user {request.user.username}.")
    messages.success(request, "Successfully connected to Google Calendar!")
    return redirect('home')

@login_required
def google_calendar_revoke_view(request: HttpRequest) -> HttpResponse:
    user_profile = request.user.profile
    credentials = user_profile.get_google_credentials()
    if credentials and credentials.token:
        try:
            import requests as http_client
            revoke_url = 'https://oauth2.googleapis.com/revoke'
            response = http_client.post(revoke_url, params={'token': credentials.token},
                                       headers={'content-type': 'application/x-www-form-urlencoded'})
            if response.status_code == 200:
                logger.info(f"Google token successfully revoked on Google's side for {request.user.username}.")
                messages.success(request, "Google Calendar access revoked from Google.")
            else:
                logger.warning(f"Failed to revoke token on Google's side for {request.user.username}. Status: {response.status_code}, Body: {response.text[:200]}")
                messages.warning(request, f"Could not fully revoke token with Google (status: {response.status_code}), but local access will be removed.")
        except Exception as e:
            logger.error(f"Error during Google token server-side revocation for {request.user.username}: {e}")
            messages.warning(request, f"An error occurred trying to revoke Google access: {e}. Local access will be removed.")
        finally:
            user_profile.google_credentials_json = None
            user_profile.save()
            logger.info(f"Local Google credentials removed for user {request.user.username}.")
    elif user_profile.google_credentials_json:
        user_profile.google_credentials_json = None
        user_profile.save()
        logger.info(f"Malformed local Google credentials cleared for {request.user.username}.")
        messages.info(request, "Local Google Calendar connection data cleared.")
    else:
        messages.info(request, "No Google Calendar connection was active.")
    return redirect('home')