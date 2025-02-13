from django.db import models

from user.models import UserProfile, TrainingSubject


class Course(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    subject = models.ForeignKey(TrainingSubject,on_delete = models.PROTECT)
    location = models.CharField(max_length=100)
    participants = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    trainer_price = models.DecimalField(max_digits=10, decimal_places=2)
    trainer = models.OneToOneField(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_course")

    def __str__(self):
        return f"{self.name} - {self.trainer.name if self.trainer else 'No Trainer Assigned'}"