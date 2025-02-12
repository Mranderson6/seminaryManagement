from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "subject", "location", "participants", "trainer_name")
    list_filter = ("subject", "location", "date")
    search_fields = ("name", "location", "trainer__name")

    def trainer_name(self, obj):
        return obj.trainer.name if obj.trainer else "No Trainer Assigned"

    trainer_name.short_description = "Trainer"
