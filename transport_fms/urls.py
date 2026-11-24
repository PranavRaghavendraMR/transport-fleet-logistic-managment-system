"""
URL configuration for transport_fms project.
Transport Fleet & Logistics Management System (FMS)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('fleet/', include('fleet.urls')),
    path('routing/', include('routing.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('safety/', include('safety.urls')),
    path('fuel/', include('fuel.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
