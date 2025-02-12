from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile, TrainingSubject


# 1. User Registration Form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=255)
    location = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["username", "email", "name", "location", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Check if a UserProfile already exists
            profile, created = UserProfile.objects.get_or_create(
                user=user, defaults={"name": self.cleaned_data["name"], "location": self.cleaned_data["location"], "email": user.email}
            )
        return user


# 2. User Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


# 3. User Profile Form (for Updating User Information)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["name", "location", "email"]


# 4. Form to Add a Training Subject
class TrainingSubjectForm(forms.ModelForm):
    class Meta:
        model = TrainingSubject
        fields = ["name"]


# 5. Assign & Deassign Training Subjects Form
class AssignTrainingSubjectForm(forms.Form):
    training_subjects = forms.ModelMultipleChoiceField(
        queryset=TrainingSubject.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop("user_profile", None)
        super().__init__(*args, **kwargs)
        if user_profile:
            self.fields["training_subjects"].queryset = TrainingSubject.objects.exclude(users=user_profile)


class DeassignTrainingSubjectForm(forms.Form):
    training_subjects = forms.ModelMultipleChoiceField(
        queryset=TrainingSubject.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop("user_profile", None)
        super().__init__(*args, **kwargs)
        if user_profile:
            self.fields["training_subjects"].queryset = user_profile.training_subjects.all()
