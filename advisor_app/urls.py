from django.urls import path
from . import views

# It's good practice to define an app_name for namespacing,
# especially if your project grows. If you use this,
# you'll need to update url tags in templates (e.g., {% url 'advisor_app:home' %})
# and reverse() calls in views (e.g., reverse('advisor_app:home')).
# For now, to keep it simple and directly address the error, we'll omit it,
# but consider adding it later.
# app_name = 'advisor_app'

urlpatterns = [
    # This is the pattern that defines the name 'home'.
    # It maps the root path of this app's included URLs to the home_view.
    path('', views.home_view, name='home'),

    path('profile/', views.profile_view, name='profile'),

    # Google Calendar OAuth URLs
    path('calendar/auth/init/', views.google_calendar_init_view, name='google_calendar_init'),
    path('calendar/oauth2callback/', views.google_calendar_oauth2callback_view, name='google_calendar_oauth2callback'),
    path('calendar/auth/revoke/', views.google_calendar_revoke_view, name='google_calendar_revoke'),
]