import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__) # advisor_app.services.weather_service

def get_weather_data(location: str):
    """
    Fetches weather data from OpenWeatherMap API.
    Returns a dictionary with weather data or an error message.
    """
    api_key = settings.OPENWEATHERMAP_API_KEY
    if not api_key:
        logger.error("OpenWeatherMap API key is not configured.")
        return {"error": "Weather service is not configured."}
    if not location:
        logger.warning("get_weather_data called with no location.")
        return {"error": "Location not provided."}

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': location,
        'appid': api_key,
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }
    try:
        logger.debug(f"Requesting weather for {location} with params: {params}")
        response = requests.get(base_url, params=params, timeout=10) # 10-second timeout
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
        weather_json = response.json()
        logger.info(f"Successfully fetched weather for {location}.")
        return weather_json
    except requests.exceptions.Timeout:
        logger.error(f"Timeout when fetching weather for {location}.")
        return {"error": "Weather service request timed out."}
    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code
        logger.error(f"HTTP error {status_code} for {location}: {http_err}. Response: {http_err.response.text}")
        if status_code == 401:
            return {"error": "Invalid API key for weather service."}
        elif status_code == 404:
            return {"error": f"City not found: {location}."}
        else:
            return {"error": f"Weather service error (HTTP {status_code})."}
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception for {location}: {req_err}")
        return {"error": "Could not connect to weather service."}
    except ValueError as json_err: # Includes JSONDecodeError
        logger.error(f"JSON decode error for {location} weather response: {json_err}")
        return {"error": "Invalid response from weather service."}