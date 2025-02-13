from django import forms
from user.models import UserProfile, TrainingSubject
from services.models import Course

class CourseForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'course-date'}), 
        required=True
    )
    participants = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}), 
        required=True
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), 
        required=True
    )
    trainer_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), 
        required=True
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), 
        required=False
    )

    subject = forms.ModelChoiceField(
        queryset=TrainingSubject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'course-subject'}),
        required=True
    )

    trainer = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(is_moderator=False),
        widget=forms.Select(attrs={'class': 'form-control trainer-dropdown', 'id': 'course-trainer'}),
        required=False
    )

    class Meta:
        model = Course
        fields = ["name", "date", "subject", "location", "participants", "notes", "price", "trainer_price", "trainer"]
        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control', 'id': 'course-name'}),
            "location": forms.TextInput(attrs={'class': 'form-control', 'id': 'course-location'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_trainer_choices()

    def update_trainer_choices(self, subject=None):
        """
        Update the trainer dropdown choices based on the selected subject and trainer availability.
        """
        trainers = UserProfile.objects.filter(is_moderator=False)
        ranked_trainers = []

        for trainer in trainers:
            match_percentage = self.get_match_percentage(trainer, subject)
            is_available = not Course.objects.filter(trainer=trainer, date=self.instance.date).exists()
            ranked_trainers.append((match_percentage, is_available, trainer))

        # Sort trainers by highest match percentage first
        ranked_trainers.sort(reverse=True, key=lambda x: (x[0], x[1]))  

        self.fields["trainer"].choices = [
            (trainer.id, f"{trainer.name} - {match_percentage}% match {'(Available)' if is_available else '(Booked)'}")
            for match_percentage, is_available, trainer in ranked_trainers
        ]

    def get_match_percentage(self, trainer, subject=None):
        """
        Calculate the percentage of match between a trainer's subjects and the course subject.
        """
        if not subject:
            return 0  # No subject selected yet

        trainer_subjects = trainer.training_subjects.all()
        if subject in trainer_subjects:
            return 100  # Perfect match

        total_subjects = trainer_subjects.count()
        if total_subjects == 0:
            return 0

        match_percentage = int((1 / total_subjects) * 100)
        return match_percentage
