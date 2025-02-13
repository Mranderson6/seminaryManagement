from django.urls import path
from .views import (
    register,
    login_view,
    logout_view,
    profile_view,
    moderator_dashboard,
    add_training_subject,
    assign_training_subject,
    deassign_training_subject, register_trainer, toggle_user_status, get_trainers_by_subject
)

urlpatterns = [
    path("register/", register, name="register"),
    path("register-trainer/", register_trainer, name="register_trainer"),  # ✅ New Trainer Registration URL
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("moderator/", moderator_dashboard, name="moderator_dashboard"),
    path("moderator/add-subject/", add_training_subject, name="add_training_subject"),
    path("moderator/assign-subject/<int:user_id>/", assign_training_subject, name="assign_training_subject"),
    path("moderator/deassign-subject/<int:user_id>/", deassign_training_subject, name="deassign_training_subject"),
    path("moderator/toggle-user-status/<int:user_id>/", toggle_user_status, name="toggle_user_status"),
    path("get-trainers-by-subject/<int:subject_id>/", get_trainers_by_subject, name="get_trainers_by_subject"),


]
