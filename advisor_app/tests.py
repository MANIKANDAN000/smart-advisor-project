from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile
from unittest.mock import patch # For mocking API calls

class UserProfileModelTests(TestCase):
    def test_profile_creation_signal(self):
        """Test that a UserProfile is created when a User is created."""
        user = User.objects.create_user(username='testuser1', password='password123')
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.user, user)

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser2', password='password123', email='test@example.com')
        # UserProfile should be created by the signal
        self.profile = self.user.profile
        self.profile.location = "London,UK"
        self.profile.save()

    def test_home_view_anonymous_redirects_to_login(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, f"{reverse('login')}?next=/")

    @patch('advisor_app.services.weather_service.get_weather_data')
    @patch('advisor_app.services.google_calendar_service.get_calendar_events')
    @patch('advisor_app.services.eventbrite_service.get_eventbrite_events')
    def test_home_view_authenticated(self, mock_eventbrite, mock_calendar, mock_weather):
        # Mock API responses
        mock_weather.return_value = {'main': {'temp': 15}, 'weather': [{'description': 'cloudy', 'icon': '04d'}]}
        mock_calendar.return_value = {'events': [{'summary': 'Test Event'}]}
        mock_eventbrite.return_value = {'events': [{'name': {'text': 'Local Fair'}}]}

        self.client.login(username='testuser2', password='password123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'advisor_app/home.html')
        self.assertContains(response, "London,UK")
        self.assertContains(response, "cloudy") # From mock weather
        # mock_weather.assert_called_once_with("London,UK") # Check service call

    def test_profile_view_get(self):
        self.client.login(username='testuser2', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'advisor_app/profile.html')
        self.assertContains(response, self.user.profile.location)

    def test_profile_view_post_update_location(self):
        self.client.login(username='testuser2', password='password123')
        new_location = "Paris,FR"
        response = self.client.post(reverse('profile'), {'location': new_location})
        self.assertRedirects(response, reverse('profile'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.location, new_location)