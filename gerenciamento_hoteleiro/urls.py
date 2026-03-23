from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # O correto é .urls e não .back
    path('', include('hotel.urls')),
]