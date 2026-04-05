from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin','Admin'),
        ('supervisor','Supervisor'),
        ('therapist','Therapist'),
        ('patient', 'Patient'),
        
    )
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='patient')

    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='therapists'
    )

    therapist = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients'
    )

    def __str__(self):
        return self.username
    


