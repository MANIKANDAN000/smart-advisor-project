
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Define an inline admin descriptor for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_location')
    list_select_related = ('profile',) # Optimize query

    def get_location(self, instance):
        return instance.profile.location
    get_location.short_description = 'Location'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Optionally, if you want a separate admin for UserProfile (though inline is often better)
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'location', 'has_google_credentials')
#     search_fields = ('user__username', 'location')
#
#     def has_google_credentials(self, obj):
#         return bool(obj.google_credentials_json)
#     has_google_credentials.boolean = True
