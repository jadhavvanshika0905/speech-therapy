from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login_page'),
    path('register/', views.register_view, name='register_page'), 
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('supervisor_dashboard',views.supervisor_dashboard,name='supervisor_dashboard'),
    path('therapist_dashboard',views.therapist_dashboard,name='therapist_dashboard'),
    path('add_user',views.add_user_view,name="add_user"),
    path('edit_user/<int:id>/',views.edit_user_view,name="edit_user"),
    path('delete_user/<int:id>/',views.delete_user_view,name="delete_user"),
    path('disable_user/<int:id>/',views.disable_user_view,name="disable_user"),
    path('enable_user/<int:id>/',views.enable_user_view,name="enable_user"),
    path('assign_therapist/', views.assign_therapist, name='assign_therapist'),
    path('assign_supervisor/', views.assign_supervisor, name='assign_supervisor'),
    path('logout',views.logout_view,name='logout'),
]