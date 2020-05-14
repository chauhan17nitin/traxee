from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^flipkart/', include('flipkart.urls')),
    url(r'^', include('flipkart.urls')),
]
