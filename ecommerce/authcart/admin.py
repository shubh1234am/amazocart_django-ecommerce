from django.contrib import admin
from .models import UserProfile  # ✅ Use the correct model name

# Register the UserProfile model to appear in Django Admin
admin.site.register(UserProfile)
