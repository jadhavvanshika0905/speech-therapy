from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from authentication.models import User
from .models import Therapist,Supervisor
from django.contrib.auth.decorators import login_required
from therapy.models import Patient,Report,Session,TherapyPlan,Notification,SupervisorFeedback,SessionMessage



# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            print("ROLE:", getattr(user, 'role', 'NO ROLE'))

            if user.is_superuser or user.role == 'admin':
                return redirect('admin_dashboard')

            elif user.role == 'supervisor':
                return redirect('supervisor_dashboard')

            elif user.role == 'therapist':
                return redirect('therapist_dashboard')

            elif user.role == 'patient':
                return redirect('patient_dashboard')

            else:
                return redirect('home_page')

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")
        age = request.POST.get("age")
        contact = request.POST.get("contact")
        issue = request.POST.get("issue")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role.lower()
            )

            if role.lower() == "patient":
                Patient.objects.create(
                    user=user,
                    name=username,
                    age=age,
                    contact=contact,
                    speech_issue=issue
                )

            messages.success(request, "User created successfully")
            return redirect('login_page')

        except Exception as e:
            print(e)
            messages.error(request, "User creation failed")
            return redirect('login_page')

    return render(request, "register.html")

def admin_dashboard(request):
    users = User.objects.all()

    therapists = User.objects.filter(role='therapist')
    supervisors = User.objects.filter(role='supervisor')
    patients_users = User.objects.filter(role='patient')
    patients = User.objects.filter(role='patient').select_related('therapist')

    context = {
        'users': users,
        'therapists_list': therapists,
        'supervisors_list': supervisors,
        'patients_list': patients,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'therapists': users.filter(role='therapist').count(),
        'patient': users.filter(role='patient').count(),
        'supervisor': users.filter(role='supervisor').count(),
        'admin': users.filter(role='admin').count(),
    }
    
    return render(request, 'admin_dashboard.html', context)

from therapy.models import Patient, Session
from django.db.models import Count


@login_required
def supervisor_dashboard(request):
    supervisor = request.user

    if supervisor.role != 'supervisor':
        return redirect('login')

    therapist_users = User.objects.filter(role='therapist', supervisor=supervisor)
    patients = Patient.objects.filter(
        assigned_therapist__in=therapist_users
    ).select_related('assigned_therapist')

    therapist_profiles = Therapist.objects.filter(
        user__in=therapist_users
    ).select_related('user').annotate(
        total_patients=Count('user__assigned_patients')
    )

    pending_plans = TherapyPlan.objects.filter(
        therapist__in=therapist_users,
        status='pending'
    )
    reports = Report.objects.filter(
        plan__therapist__in=therapist_users
    ).select_related('plan', 'plan__patient', 'plan__therapist')

    unread_notifications = Notification.objects.filter(
        user=supervisor,
        is_read=False
    )

    context = {
        "therapist_count":     therapist_users.count(),
        "patient_count":       patients.count(),
        "completed":           patients.filter(status='completed').count(),
        "ongoing":             patients.filter(status='ongoing').count(),
        "therapist_profiles":  therapist_profiles,
        "patients":            patients,
        "pending_plans_count": pending_plans.count(),
        "unread_count":        unread_notifications.count(),
        "notifications":       unread_notifications[:5],
        "reports":             reports,
    }

    return render(request, "supervisor_dashboard.html", context)


@login_required
def therapist_dashboard(request):    
    patients = Patient.objects.filter(assigned_therapist=request.user)
    plans = TherapyPlan.objects.filter(therapist=request.user).select_related('patient')
    total     = patients.count()
    completed = patients.filter(status='completed').count()
    ongoing   = patients.filter(status='ongoing').count()

    # Har patient ke liye active_session_id aur unread_count
    for patient in patients:
        # ✅ FIX: Session.plan.patient ke through filter karo
        session = Session.objects.filter(plan__patient=patient).order_by('-id').first()
        patient.active_session_id = session.id if session else None

        if session:
            patient.unread_count = SessionMessage.objects.filter(
                session=session,
                is_read=False,
            ).exclude(sender=request.user).count()
        else:
            patient.unread_count = 0

    feedbacks = SupervisorFeedback.objects.filter(
        plan__therapist=request.user
    ).select_related('plan', 'plan__patient').order_by('-id')
    
    reports = Report.objects.filter(
        plan__therapist=request.user
    ).select_related('plan', 'plan__patient')

    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    context = {
        'patients':      patients,
        'total':         total,
        'plans':         plans,
        'completed':     completed,
        'ongoing':       ongoing,
        'pending_plans': plans.filter(status='pending').count(),
        'unread_count':  unread_notifications.count(),
        'notifications': unread_notifications[:5],
        'feedbacks':     feedbacks,
        'reports':       reports,
    }
    return render(request, 'therapist_dashboard.html', context)


def add_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )

        if role == "therapist":
            Therapist.objects.create(
                user=user,
                full_name=username,
                specialization=request.POST.get("specialization"),
                qualification=request.POST.get("qualification"),
                experience_years=request.POST.get("experience") or 0
            )

        elif role == "patient":
            Patient.objects.create(
                user=user,
                name=username,
                age=request.POST.get("age"),
                contact=request.POST.get("contact"),
                speech_issue=request.POST.get("issue")
            )

        elif role == "supervisor":
            Supervisor.objects.create(
                user=user,
                full_name=username,
                contact=request.POST.get("contact"),
                experience_years=request.POST.get("experience_supervisor") or 0,
                department=request.POST.get("department"),
            )

        return redirect('login_page')
    return render(request, "add_user.html")

    
def edit_user_view(request, id):
    user = User.objects.get(id=id)

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        password = request.POST.get("password")
        user.role = request.POST.get("role")

        if password:
            user.set_password(password)

        user.save()
        return redirect('admin_dashboard')

    return render(request, 'edit_user.html', {'user': user})

def delete_user_view(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect("admin_dashboard")

def disable_user_view(request, id):
    user = User.objects.get(id=id)
    user.is_active = False
    user.save()
    return redirect("admin_dashboard")

def enable_user_view(request, id):
    user = User.objects.get(id=id)
    user.is_active = True
    user.save()
    return redirect("admin_dashboard")

def logout_view(request):
    logout(request)
    return redirect('login_page')

def assign_therapist(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        therapist_id = request.POST.get('therapist_id')
        
        patient_user = User.objects.get(id=patient_id, role='patient')
        therapist = User.objects.get(id=therapist_id, role='therapist')

        patient_user.therapist = therapist
        patient_user.save()

        try:
            patient_profile = Patient.objects.get(user=patient_user)
            patient_profile.assigned_therapist = therapist
            patient_profile.save()
        except Patient.DoesNotExist:
            Patient.objects.create(
                user=patient_user,
                name=patient_user.username,
                contact=patient_user.email,
                assigned_therapist=therapist
            )

        return redirect('admin_dashboard')

    patients = User.objects.filter(role='patient')
    therapists = User.objects.filter(role='therapist')

    return render(request, 'assign_therapist.html', {
        'patients': patients,
        'therapists': therapists
    })

def assign_supervisor(request):
    if request.method == "POST":
        therapist_id = request.POST.get("therapist_id")
        supervisor_id = request.POST.get("supervisor_id")

        therapist = User.objects.get(id=therapist_id, role='therapist')
        supervisor = User.objects.get(id=supervisor_id, role='supervisor')

        therapist.supervisor = supervisor
        therapist.save()

        return redirect('admin_dashboard')

    therapists = User.objects.filter(role='therapist')
    supervisors = User.objects.filter(role='supervisor')

    return render(request, 'assign_supervisor.html', {
        'therapists': therapists,
        'supervisors': supervisors
    })