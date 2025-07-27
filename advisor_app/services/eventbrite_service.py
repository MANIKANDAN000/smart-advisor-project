# smart_advisor_project/advisor_app/services/eventbrite_service.py

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_eventbrite_events(location_address: str = None, latitude: float = None, longitude: float = None):
    api_key = settings.EVENTBRITE_API_KEY
    if not api_key:
        logger.error("Eventbrite API key is not configured in settings.py.")
        return {"error": "Eventbrite service is not configured (API key missing)."}

    if not location_address and not (latitude and longitude):
        logger.warning("get_eventbrite_events called with no location information.")
        return {"error": "Location (address or lat/lon) must be provided for Eventbrite."}

    base_url = "https://www.eventbriteapi.com/v3/events/search/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    params = {
        'sort_by': 'date',
        'expand': 'venue,organizer,ticket_availability,format'
    }

    current_search_location = ""
    if location_address:
        params['location.address'] = location_address
        current_search_location = location_address
        logger.debug(f"Requesting Eventbrite events for address: {location_address} using API key ending with ...{api_key[-4:] if api_key else 'N/A'}")
    elif latitude and longitude:
        params['location.latitude'] = str(latitude)
        params['location.longitude'] = str(longitude)
        params['location.within'] = '25km' # Default radius
        current_search_location = f"lat/lon: {latitude},{longitude}"
        logger.debug(f"Requesting Eventbrite events for {current_search_location} using API key ending with ...{api_key[-4:] if api_key else 'N/A'}")

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=15)
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
        data = response.json()
        events = data.get('events', [])
        logger.info(f"Successfully fetched {len(events)} Eventbrite events for location: {current_search_location}.")
        return {"events": events}
    except requests.exceptions.Timeout:
        logger.error(f"Request to Eventbrite API timed out for location: {current_search_location}.")
        return {"error": "Eventbrite service request timed out."}
    except requests.exceptions.HTTPError as http_err:
        error_content = http_err.response.text
        status_code = http_err.response.status_code
        logger.error(f"Eventbrite HTTP error {status_code} for location: {current_search_location}: {http_err}. Response: {error_content[:500]}")
        try:
            error_json = http_err.response.json()
            error_desc = error_json.get('error_description', error_json.get('error', 'Unknown Eventbrite API error'))
            
            # Specific handling for the "path does not exist" 404 error from Eventbrite
            if error_json.get('error') == "NOT_FOUND" and "path you requested does not exist" in error_desc.lower():
                # This is the error you are seeing. It means Eventbrite doesn't like the location.address value.
                return {"error": "Eventbrite could not find events for the specified location. Please try a more specific city or area. (Hint: country names like 'India' might be too broad for Eventbrite's address search)."}
            elif "LOCATION_INVALID" in error_json.get('error', ''):
                 return {"error": "Invalid location format for Eventbrite. Please try a specific city name. (API: Location Invalid)"}
            
            return {"error": f"Eventbrite API Error: {error_desc}"}
        except ValueError: # If response from Eventbrite isn't valid JSON
            if status_code == 404:
                 # Generic 404 if not the specific "path does not exist" message
                 return {"error": "Eventbrite could not find information for the specified location (404). Please try being more specific."}
            return {"error": f"Eventbrite service error (HTTP {status_code}). Response was not valid JSON."}
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Eventbrite request exception for location: {current_search_location}: {req_err}")
        return {"error": "Could not connect to Eventbrite service."}
    except ValueError as json_err: # Includes JSONDecodeError if response.json() fails
        logger.error(f"Eventbrite JSON decode error for location: {current_search_location}: {json_err}")
        return {"error": "Invalid response format from Eventbrite service."}