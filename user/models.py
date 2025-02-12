from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    training_subjects = models.ManyToManyField("TrainingSubject", related_name="users")  # Connect subjects
    location = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_moderator = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TrainingSubject(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Training subject name

    def __str__(self):
        return self.name
