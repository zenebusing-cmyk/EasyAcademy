
from django.contrib import admin
from django.urls import path, include
from students import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Public homepage
    path("", views.home, name="home"),

    # Existing student management pages
    path("students/", include("students.urls")),
]
