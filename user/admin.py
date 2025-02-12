from django.contrib import admin
from .models import UserProfile, TrainingSubject

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "location", "is_moderator")
    list_filter = ("is_moderator", "location")
    search_fields = ("name", "email")

@admin.register(TrainingSubject)
class TrainingSubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
