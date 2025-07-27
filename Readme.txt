Personalized Smart Weather & Activity Advisor
A Django-powered web application designed to provide users with personalized weather forecasts, upcoming Google Calendar events, and local Eventbrite activities, helping them plan their day effectively.
This project integrates multiple external APIs to fetch real-time data and presents it in a user-friendly dashboard. Users can set their location, connect their Google Calendar, and receive tailored suggestions.
Core Features:
User Authentication: Secure login and registration (using Django's built-in auth system).
Personalized Dashboard: A central view displaying:
Current Weather: Fetched using the OpenWeatherMap API, showing temperature, conditions, humidity, and wind speed based on the user's saved location.
Upcoming Google Calendar Events: Securely connects via Google OAuth 2.0 to display a list of the user's upcoming calendar events.
Local Eventbrite Events: Fetches local events from Eventbrite based on the user's location.
User Profile Management: Allows users to set and update their primary location for weather and event fetching.
Google OAuth 2.0 Integration: Securely manages Google Calendar authentication, including token refresh and revocation.
Responsive Design (Basic): Styled with global CSS for a clean and usable interface on different devices.
Technologies & APIs Used:
Backend:
Python 3.12+
Django Framework (v4.2.x): For the core web application structure, ORM, templating, and request handling.
django.contrib.auth: For user authentication and management.
django.contrib.sessions: For session management.
django.contrib.messages: For displaying feedback to users.
python-dotenv: To manage environment variables and API keys securely.
requests: For making HTTP requests to external APIs.
External APIs:
OpenWeatherMap API:
* Purpose: To fetch current weather data.
* Endpoint Used: api.openweathermap.org/data/2.5/weather
* Authentication: API Key.
Google Calendar API (via Google API Python Client):
* Purpose: To access users' primary calendar and fetch upcoming events.
* Authentication: OAuth 2.0 (with google-auth-oauthlib and google-api-python-client).
* Scopes Used: https://www.googleapis.com/auth/calendar.readonly
* Key Libraries:
google-api-python-client: To interact with the Google Calendar API.
google-auth-oauthlib: To handle the OAuth 2.0 flow for web server applications.
google-auth-httplib2: Often a dependency for google-auth.
Eventbrite API:
* Purpose: To discover local events based on user location.
* Endpoint Used: https://www.eventbriteapi.com/v3/events/search/
* Authentication: OAuth 2.0 Bearer Token (API Key used as a bearer token).
Frontend (Basic):
HTML5
CSS3: Custom global stylesheet for basic styling.
Django Template Language: For dynamic content rendering.
Database:
SQLite3: Default Django database, suitable for development and small-scale deployments. (Can be easily swapped for PostgreSQL, MySQL, etc., for production).
Development Environment & Tools:
Virtual Environment (venv): To manage project dependencies.
Git & GitHub: For version control and code hosting.
OAUTHLIB_INSECURE_TRANSPORT=1: Environment variable (or in-code setting for DEBUG) used during local development to allow Google OAuth token exchange over HTTP. This is for development only and must not be used in production.

smart_advisor_project/
├── .env                       # Stores API keys and sensitive configurations
├── manage.py                  # Django's command-line utility
├── requirements.txt           # Project dependencies
├── smart_advisor_project/     # Django project configuration package
│   ├── settings.py            # Project settings
│   ├── urls.py                # Project-level URL routing
│   └── ...
├── advisor_app/               # Main application package
│   ├── models.py              # Database models (e.g., UserProfile)
│   ├── views.py               # Request handling logic
│   ├── urls.py                # App-level URL routing
│   ├── services/              # Business logic for interacting with external APIs
│   │   ├── weather_service.py
│   │   ├── google_calendar_service.py
│   │   └── eventbrite_service.py
│   ├── templates/             # HTML templates for the app
│   │   └── advisor_app/
│   ├── signals.py             # For Django signals (e.g., auto-creating UserProfile)
│   └── ...
├── staticfiles/               # Global static files (CSS, JS, images) for development
│   └── css/
│       └── global_styles.css
└── templates/                 # Global project templates
    └── registration/
        └── login.html         # Custom login page template

Google Cloud Console Setup for OAuth:
Create a project in Google Cloud Console.
Enable the Google Calendar API.
Create an OAuth 2.0 Client ID for a "Web application".
Add http://127.0.0.1:8000 to "Authorized JavaScript origins" (if you plan to use client-side JS for OAuth later, not strictly needed for this server-side flow).
Add http://127.0.0.1:8000/calendar/oauth2callback/ to "Authorized redirect URIs".
Configure the OAuth consent screen:
Set to "External" user type.
During development, keep "Publishing status" as "Testing" and add your Google account email(s) to the "Test users" list to avoid "access_denied" errors.
Future Enhancements (Potential):
More sophisticated "advisor" logic to suggest activities based on weather and calendar.
User preferences for activity types.
Geolocation for automatic location detection.
Integration with other calendar/task services.
Improved UI/UX with a frontend framework (e.g., React, Vue, or Bootstrap/Tailwind).
Asynchronous task handling for API calls (e.g., using Celery).
Caching for API responses.
Comprehensive unit and integration tests.
Deployment to a cloud platform (e.g., Heroku, AWS, Google Cloud Run).
Contribution:
(Optional: Add guidelines if you want others to contribute)
Feel free to fork this repository, make improvements, and submit pull requests. Please follow standard coding practices and ensure tests pass (if applicable).