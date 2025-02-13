from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from core.utils import has_schedule_conflict, suggest_best_trainer
from user.models import TrainingSubject
from .models import Course, UserProfile
from .forms import CourseForm
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.views.decorators.http import require_GET



#  1. List All Courses
def course_list(request):
    courses = Course.objects.all()
    return render(request, "course_list.html", {"courses": courses})



def is_moderator(user):
    return hasattr(user, "userprofile") and user.userprofile.is_moderator

@login_required
@user_passes_test(is_moderator)
def course_create(request, course_id=None):
    """
    Creates or edits a course:
      - Prevents assigning the same trainer to multiple courses on the same day.
      - Ensures the trainer is qualified for the subject.
      - Warns if a trainer has a low match percentage.
      - Suggests another trainer if the selected one is unavailable.
      - Updates 'is_affiliated' dynamically when a course is assigned or removed.
      - Sends success/error/conflict JSON for SweetAlert.
    """
    course = None
    previous_trainer = None

    if course_id:
        course = get_object_or_404(Course, id=course_id)
        previous_trainer = course.trainer  # Store the existing trainer before updates

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            selected_trainer = form.cleaned_data.get("trainer")  # Selected trainer
            selected_subject = form.cleaned_data.get("subject")  # Selected subject
            course_date = form.cleaned_data.get("date")  # Selected date

            # 1) Prevent assigning a trainer to multiple courses on the same date
            if selected_trainer and Course.objects.filter(trainer=selected_trainer, date=course_date).exclude(id=course_id).exists():
                return JsonResponse({
                    "status": "error",
                    "message": f"Trainer {selected_trainer.name} is already scheduled for another course on {course_date}. Choose another trainer."
                })

            # 2) Ensure the trainer is qualified for the subject
            warning_message = ""
            if selected_trainer and selected_subject not in selected_trainer.training_subjects.all():
                warning_message = f"⚠️ Warning: Trainer {selected_trainer.name} is not fully qualified for '{selected_subject.name}'."

            # 3) Calculate the match percentage
            match_percentage = form.get_match_percentage(selected_trainer, selected_subject)

            # 4) If the match percentage is below 50%, show a warning
            if match_percentage < 50:
                warning_message += f" Trainer {selected_trainer.name} has a low match of {match_percentage}%. This selection is **not recommended**."

            # 5) Check for scheduling conflicts
            if selected_trainer and has_schedule_conflict(selected_trainer, course_date):
                suggested = suggest_best_trainer(selected_subject, course_date)
                if suggested:
                    return JsonResponse({
                        "status": "conflict",
                        "message": f"Trainer {selected_trainer.name} is already booked on {course_date}. Suggested Trainer: {suggested.name}."
                    })
                else:
                    return JsonResponse({
                        "status": "conflict",
                        "message": f"No available trainer for {selected_subject.name} on {course_date}. Please choose a different date or trainer."
                    })

            # 6) Save the course and update trainer affiliation status
            course = form.save(commit=False)
            course.trainer = selected_trainer
            course.save()

            # 7) Update trainer's `is_affiliated` status
            if selected_trainer:
                selected_trainer.is_affiliated = True  # Trainer is now assigned to a course
                selected_trainer.save()

            # 8) If previous trainer was replaced, update their affiliation status
            if previous_trainer and previous_trainer != selected_trainer:
                if not Course.objects.filter(trainer=previous_trainer).exists():
                    previous_trainer.is_affiliated = False
                    previous_trainer.save()

            # 9) Send an email notification to the assigned trainer
            if course.trainer:
                subject = f"🚀 Assigned to a New Course: {course.name}"
                message = (
                    f"Hello {course.trainer.name},\n\n"
                    f"You have been assigned as the trainer for **'{course.name}'** on **{course.date}**.\n\n"
                    f"📌 Course Details:\n"
                    f"- **Subject**: {course.subject.name}\n"
                    f"- **Location**: {course.location}\n"
                    f"- **Participants**: {course.participants}\n"
                    f"- **Notes**: {course.notes if course.notes else 'None'}\n\n"
                    f"📢 Please prepare accordingly.\n\n"
                    f"Best Regards,\n"
                    f"Seminar Management Team"
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [course.trainer.email],
                    fail_silently=False
                )

            # Return success response, including any warnings
            response_data = {
                "status": "success",
                "message": f"✅ Course '{course.name}' has been successfully {'created' if not course_id else 'updated'}!"
            }
            if warning_message:
                response_data["warning"] = warning_message  # Include warning message if applicable

            return JsonResponse(response_data)
        else:
            # Handle form errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field.capitalize()}: {error}")

            return JsonResponse({
                "status": "error",
                "message": " ".join(error_messages)
            })

    return render(request, "course_form.html", {"form": CourseForm(instance=course)})



@require_GET
def get_trainers_by_subject(request):
    subject_id = request.GET.get("subject_id")
    date = request.GET.get("date")

    if not subject_id or not date:
        return JsonResponse({"error": "Missing subject or date parameter"}, status=400)

    try:
        subject = TrainingSubject.objects.get(id=subject_id)
    except TrainingSubject.DoesNotExist:
        return JsonResponse({"error": "Subject not found"}, status=404)

    trainers = UserProfile.objects.filter(is_moderator=False, training_subjects=subject)

    trainer_list = []
    for trainer in trainers:
        trainer_subjects = set(trainer.training_subjects.all())
        match_percentage = 100 if subject in trainer_subjects else int((1 / len(trainer_subjects)) * 100) if trainer_subjects else 0
        is_available = not Course.objects.filter(trainer=trainer, date=date).exists()

        trainer_list.append({
            "id": trainer.id,
            "name": trainer.name,
            "match_percentage": match_percentage,
            "available": is_available
        })

    # Sort trainers by match percentage descending
    trainer_list.sort(key=lambda x: x["match_percentage"], reverse=True)

    return JsonResponse({"trainers": trainer_list})


def get_match_percentage(trainer, subject):
    """
    Calculate the match percentage between a trainer's subjects and the selected course subject.
    """
    trainer_subjects = trainer.training_subjects.all()
    if subject in trainer_subjects:
        return 100  # Perfect match

    total_subjects = len(trainer_subjects)
    if total_subjects == 0:
        return 0

    return int((1 / total_subjects) * 100)

@login_required
@user_passes_test(is_moderator)
def delete_course(request, course_id):
    """
    Deletes a course and updates the trainer's affiliation status.
    """
    course = get_object_or_404(Course, id=course_id)
    trainer = course.trainer  # Store trainer before deleting course

    if request.method == "POST":
        course.delete()

        # If the trainer has no more assigned courses, update affiliation status
        if trainer and not Course.objects.filter(trainer=trainer).exists():
            trainer.is_affiliated = False
            trainer.save()

        messages.success(request, "Course deleted successfully!")
        return redirect("moderator_dashboard")

    return JsonResponse({"error": "Invalid request method"}, status=400)