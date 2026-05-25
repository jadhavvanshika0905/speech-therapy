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


class Therapist(models.Model):
    # 🔗 Connection with User
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='therapist_profile' )
    # 👤 Basic Info
    full_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, blank=True)

    # 🎓 Professional Info
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField()

    # 🕒 Work Info
    availability = models.CharField(max_length=100, blank=True)  
    # Example: "Mon-Fri 10AM-5PM"

    supervisor = models.ForeignKey(
        'Supervisor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='therapists'
    )


    # ⭐ Performance
    rating = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)

    # 📅 Meta
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
class Supervisor(models.Model):
    # 🔗 Link with User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='supervisor_profile'
    )

    # 👤 Basic Info
    full_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)

    # 🏢 Professional Info
    department = models.CharField(max_length=100)
    experience_years = models.IntegerField()

    # 📊 Work Info
    total_therapists_managed = models.IntegerField(default=0)

    # 📅 Meta
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    


