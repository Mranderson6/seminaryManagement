from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import UserProfile, TrainingSubject
from .forms import (
    UserRegistrationForm,
    LoginForm,
    UserProfileForm,
    TrainingSubjectForm,
    AssignTrainingSubjectForm,
    DeassignTrainingSubjectForm,
)


#  Check if User is a Moderator
def is_moderator(user):
    return hasattr(user, "userprofile") and user.userprofile.is_moderator


#  1. User Registration View
def register(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already registered and logged in.")
        return redirect("profile")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Registration failed. Please check the form and try again.")
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})


#  2. User Login View
def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("profile")

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("profile")
            else:
                messages.error(request, "Invalid username or password. Please try again.")
        else:
            messages.error(request, "Form submission failed. Check the fields and try again.")

    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


#  3. User Logout View
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("login")


#  4. User Profile View (Update Profile)
@login_required
def profile_view(request):
    profile = request.user.userprofile
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Error updating profile. Please check the form.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "profile.html", {"form": form})


#  5. Moderator Dashboard (Manage Users & Training Subjects)
@login_required
@user_passes_test(is_moderator)
def moderator_dashboard(request):
    users = UserProfile.objects.all()
    subjects = TrainingSubject.objects.all()
    return render(request, "moderator_dashboard.html", {"users": users, "subjects": subjects})


#  6. Add Training Subject (Only Moderators)
@login_required
@user_passes_test(is_moderator)
def add_training_subject(request):
    if request.method == "POST":
        form = TrainingSubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Training subject added successfully!")
            return redirect("moderator_dashboard")
        else:
            messages.error(request, "Failed to add training subject. Please check the form.")
    else:
        form = TrainingSubjectForm()

    return render(request, "training_subject_form.html", {"form": form})


#  7. Assign Training Subjects to User (Only Moderators)
@login_required
@user_passes_test(is_moderator)
def assign_training_subject(request, user_id):
    trainer = get_object_or_404(UserProfile, id=user_id)

    if request.method == "POST":
        form = AssignTrainingSubjectForm(request.POST, user_profile=trainer)
        if form.is_valid():
            trainer.training_subjects.add(*form.cleaned_data["training_subjects"])
            messages.success(request, f"Training subjects assigned to {trainer.name} successfully!")
            return redirect("moderator_dashboard")
        else:
            messages.error(request, "Failed to assign training subjects.")
    else:
        form = AssignTrainingSubjectForm(user_profile=trainer)

    return render(request, "assign_training_subject.html", {"form": form, "trainer": trainer})


#  8. Deassign Training Subjects from User (Only Moderators)
@login_required
@user_passes_test(is_moderator)
def deassign_training_subject(request, user_id):
    trainer = get_object_or_404(UserProfile, id=user_id)

    if request.method == "POST":
        form = DeassignTrainingSubjectForm(request.POST, user_profile=trainer)
        if form.is_valid():
            trainer.training_subjects.remove(*form.cleaned_data["training_subjects"])
            messages.success(request, f"Training subjects removed from {trainer.name} successfully!")
            return redirect("moderator_dashboard")
        else:
            messages.error(request, "Failed to remove training subjects.")
    else:
        form = DeassignTrainingSubjectForm(user_profile=trainer)

    return render(request, "deassign_training_subject.html", {"form": form, "trainer": trainer})
