from django.contrib import admin
from django.urls import path, include # Ensure 'include' is imported
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # This line includes all URL patterns from advisor_app.urls.py.
    # Since 'home' is defined as path '' in advisor_app.urls.py,
    # and we are including it at the project's root path '',
    # the 'home' URL will be accessible at http://127.0.0.1:8000/
    path('', include('advisor_app.urls')), # This makes 'home' available

    # Authentication URLs
    path('login/',
         auth_views.LoginView.as_view(
             template_name='registration/login.html' # Points to your custom login template
         ),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(
             next_page='login' # Redirect to the login page after logout
         ),
         name='logout'),

    # Example for future password reset (keep commented if not implemented yet)
    # path('password-reset/',
    #      auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
    #      name='password_reset'),
    # path('password-reset/done/',
    #      auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
    #      name='password_reset_done'),
    # path('password-reset-confirm/<uidb64>/<token>/',
    #      auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
    #      name='password_reset_confirm'),
    # path('password-reset-complete/',
    #      auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
    #      name='password_reset_complete'),
]