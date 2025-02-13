from django.urls import path
from .views import course_list, course_create, get_trainers_by_subject
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("courses/", course_list, name="course_list"),
    path("courses/new/", course_create, name="course_create"),
    path("edit/<int:course_id>/", course_create, name="course_edit"),
    path("get_trainers_by_subject/", get_trainers_by_subject, name="get_trainers_by_subject"),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)