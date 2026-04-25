from django.urls import path
from . import views

urlpatterns = [
    path('add-patient/', views.add_patient, name='add_patient'),
    path('patients/', views.patient_list, name='patient_list'),
    path('create-plan/', views.create_plan, name='create_plan'),
    path('plans/', views.plan_list, name='plan_list'),
    path('submit-plan/<int:id>/', views.submit_plan, name='submit_plan'),
    path('approve-plan/<int:id>/', views.approve_plan, name='approve_plan'),
    path('therapy/add-session/<int:plan_id>/', views.add_session, name='add_session'),
    path('therapy/sessions/<int:plan_id>/', views.view_sessions, name='view_sessions'),
    path('therapy/edit-patient/<int:id>/', views.edit_patient, name='edit_patient'),
    path('therapy/delete-patient/<int:id>/', views.delete_patient, name='delete_patient'),
    path('therapy/generate-report/<int:plan_id>/', views.generate_report, name='generate_report'),
    path('therapy/approve-report/<int:id>/', views.approve_report, name='approve_report'),
    path('reports/', views.report_list, name='report_list'),
    path('therapy/report/<int:plan_id>/', views.view_report, name='view_report'),
    path('report/pdf/<int:report_id>/', views.download_report_pdf, name='download_report_pdf'),
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/feedback/<int:plan_id>/', views.add_feedback, name='add_feedback'),
    path('supervisor/feedback/edit/<int:feedback_id>/', views.edit_feedback, name='edit_feedback'),
    path('supervisor/feedback/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('certificate/<int:plan_id>/', views.generate_certificate, name='generate_certificate'),
]