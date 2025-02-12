from django.urls import path
from .views import course_list, course_create

urlpatterns = [
    path("courses/", course_list, name="course_list"),
    path("courses/new/", course_create, name="course_create"),
    path("edit/<int:course_id>/", course_create, name="course_edit"),
]
