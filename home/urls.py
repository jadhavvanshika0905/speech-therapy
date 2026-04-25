from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('therapist_dashboard/', views.therapist_dashboard, name='therapist_dashboard'),
]
