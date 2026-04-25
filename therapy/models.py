# Create your models here.
from django.db import models
from authentication.models import User 
from django.core.validators import MinValueValidator

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(0)])
    speech_issue = models.CharField(max_length=200)
    contact = models.CharField(max_length=15)
    assigned_therapist = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class TherapyPlan(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    therapist = models.ForeignKey('authentication.User', on_delete=models.CASCADE)

    exercises = models.TextField()
    goals = models.TextField()
    duration = models.IntegerField()

    is_submitted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Plan for {self.patient.name}"
    
class Session(models.Model):
    plan = models.ForeignKey(TherapyPlan, on_delete=models.CASCADE)
    session_number = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    progress = models.TextField()
    notes = models.TextField()

    def __str__(self):
        return f"Session {self.session_number} - {self.plan.patient.name}"
    
class Report(models.Model):
    plan = models.ForeignKey(TherapyPlan, on_delete=models.CASCADE)
    summary = models.TextField()
    status = models.CharField(max_length=20, default="Pending")  # Pending / Approved

    def __str__(self):
        return f"Report - {self.plan.patient.name}"
    
class SupervisorFeedback(models.Model):
    plan = models.ForeignKey(TherapyPlan, on_delete=models.CASCADE)
    feedback = models.TextField()
    rating = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.plan.patient.name}"