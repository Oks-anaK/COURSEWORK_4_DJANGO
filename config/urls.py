from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mailing/', include("mailing.urls", namespace='mailing')),
    path('users/', include("users.urls", namespace='users')),
]
