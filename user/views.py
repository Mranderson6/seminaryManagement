from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse



from services.forms import CourseForm
from services.models import Course
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


@login_required
@user_passes_test(is_moderator)
def register_trainer(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            messages.success(request, f"Trainer {user.username} created successfully!")
            return redirect("moderator_dashboard")
        else:
            messages.error(request, "Error creating trainer. Please check the form.")

    return redirect("moderator_dashboard")


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
                return redirect("moderator_dashboard" if is_moderator(user) else "profile")
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
    trainers = UserProfile.objects.filter(is_moderator=False).prefetch_related('training_subjects')
    subjects = TrainingSubject.objects.all()
    courses = Course.objects.all()

    # ✅ Fetch trainer's assigned courses properly
    trainer_courses = {trainer.id: list(Course.objects.filter(trainer=trainer)) for trainer in trainers}

    trainer_form = UserRegistrationForm()
    course_form = CourseForm()
    subject_form = TrainingSubjectForm()

    return render(request, "moderator_dashboard.html", {
        "trainers": trainers,
        "trainer_courses": trainer_courses,  # ✅ Pass trainer's courses separately
        "subjects": subjects,
        "courses": courses,
        "trainer_form": trainer_form,
        "course_form": course_form,
        "subject_form": subject_form,
    })




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
        subject_ids = request.POST.getlist("training_subjects")  # ✅ Get multiple selected subjects
        selected_subjects = TrainingSubject.objects.filter(id__in=subject_ids)

        # ✅ Update the trainer's subjects
        trainer.training_subjects.set(selected_subjects)  # Replace all assigned subjects

        messages.success(request, f"Training subjects updated for {trainer.name}!")
        return redirect("moderator_dashboard")

    messages.error(request, "Invalid form submission.")
    return redirect("moderator_dashboard")

@login_required
@user_passes_test(is_moderator)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active  # Toggle activation status
    user.save()

    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} has been {status}.")

    return redirect("moderator_dashboard")


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

@login_required
def get_trainers_by_subject(request, subject_id):
    """
    Retourne la liste des formateurs triés par adéquation avec le sujet sélectionné.
    """
    try:
        selected_subject = TrainingSubject.objects.get(id=subject_id)
    except TrainingSubject.DoesNotExist:
        return JsonResponse({"error": "Subject not found"}, status=404)

    trainers = UserProfile.objects.filter(is_moderator=False)  # Filtrer les formateurs
    trainer_list = []

    for trainer in trainers:
        trainer_subjects = set(trainer.training_subjects.all())
        fit_percentage = 0

        if selected_subject in trainer_subjects:
            fit_percentage = 100  # Correspondance parfaite
        elif trainer_subjects:
            common_subjects = trainer_subjects.intersection([selected_subject])
            total_subjects = len(trainer_subjects)
            fit_percentage = int((len(common_subjects) / total_subjects) * 100) if total_subjects > 0 else 0

        trainer_list.append({"id": trainer.id, "name": trainer.name, "fit_percentage": fit_percentage})

    # Trier par pourcentage décroissant
    trainer_list = sorted(trainer_list, key=lambda x: x["fit_percentage"], reverse=True)

    return JsonResponse({"trainers": trainer_list})