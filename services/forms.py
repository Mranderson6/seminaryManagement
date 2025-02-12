from django import forms

from user.models import UserProfile
from .models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "date", "subject", "location", "participants", "notes", "price", "trainer_price", "trainer"]
        widgets = {
            "trainer": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trainer"].queryset = UserProfile.objects.all()  # List all trainers
