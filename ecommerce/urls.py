from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   
    path('admin/', admin.site.urls),
    path('auth/', include('authcart.urls')),         # Login/Signup/Profile
    path('', include('ecommerceapp.urls')),          # Homepage, products, etc.
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
