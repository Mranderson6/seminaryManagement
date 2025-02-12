from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course, UserProfile
from .forms import CourseForm


# Check if User is a Moderator
def is_moderator(user):
    return hasattr(user, "userprofile") and user.userprofile.is_moderator


#  1. List All Courses
def course_list(request):
    courses = Course.objects.all()
    return render(request, "course_list.html", {"courses": courses})


#  2. Create or Edit a Course with Trainer Assignment & Email Notification
@login_required
@user_passes_test(is_moderator)
def course_create(request, course_id=None):
    course = None
    if course_id:
        course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()

            # If a trainer is assigned, send an email notification
            if course.trainer:
                subject = f"You have been assigned to a new course: {course.name}"
                message = f"""
                Hello {course.trainer.name},

                You have been assigned as the trainer for the course "{course.name}".

                Course Details:
                - Date: {course.date}
                - Subject: {course.subject.name}
                - Location: {course.location}
                - Participants: {course.participants}
                - Notes: {course.notes}

                Please prepare accordingly.

                Best Regards,
                Seminar Management Team
                """
                send_mail(
                    subject,
                    message,
                    "your_email@gmail.com",
                    [course.trainer.email],
                    fail_silently=False,
                )

                messages.success(request, f"{course.trainer.name} has been assigned as the trainer for {course.name}!")

            else:
                messages.info(request, "Course created without a trainer. You can assign one later.")

            return redirect("course_list")
        else:
            messages.error(request, "Error saving the course. Please check the form and try again.")

    else:
        form = CourseForm(instance=course)

    return render(request, "course_form.html", {"form": form, "course": course})
