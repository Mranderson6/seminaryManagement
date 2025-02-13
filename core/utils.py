from services.models import Course
from user.models import UserProfile, TrainingSubject


def has_schedule_conflict(trainer, course_date):
    # Filter courses by trainer and matching date
    conflict_exists = Course.objects.filter(trainer=trainer, date=course_date).exists()
    return conflict_exists


def suggest_best_trainer(subject, course_date):
    # 1. Filter trainers who have the subject in their training_subjects
    eligible_trainers = UserProfile.objects.filter(
        is_moderator=False,
        training_subjects=subject
    )

    # 2. Filter out trainers that are already booked on 'course_date'
    free_trainers = []
    for trainer in eligible_trainers:
        if not has_schedule_conflict(trainer, course_date):
            free_trainers.append(trainer)

    # 3. If no free trainer is found, return None
    if not free_trainers:
        return None

    # 4. (Optional) Choose the "best" from the free trainers
    #    For example, you might want to choose the one with the most matching subjects
    #    or the fewest scheduled courses that day/week. We'll keep it simple:
    return free_trainers[0]
