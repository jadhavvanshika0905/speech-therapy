from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .models import User


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
                return redirect('home_page')  # fallback

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def admin_dashboard(request):
    users = User.objects.all()

    therapists = User.objects.filter(role='therapist')
    supervisors = User.objects.filter(role='supervisor')
    patients = User.objects.filter(role='patient')

    
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

def supervisor_dashboard(request):
    return render(request, 'supervisor_dashboard.html')

def therapist_dashboard(request):
    return render(request, 'therapist_dashboard.html')

def add_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")
        user = User.objects.create_user(username = username,email=email,password=password,role=role)
        user.save()
        return redirect('admin_dashboard')
    return render(request,"add_user.html")
    
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

def delete_user_view(request,id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect("admin_dashboard")

def disable_user_view(request,id):
    user = User.objects.get(id=id)
    user.is_active=False
    user.save()
    return redirect("admin_dashboard")

def enable_user_view(request,id):
    user = User.objects.get(id=id)
    user.is_active=True
    user.save()
    return redirect("admin_dashboard")

def logout_view(request):
    logout(request)
    return redirect('login_page')

def assign_therapist(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        therapist_id = request.POST.get('therapist_id')
        patient = User.objects.get(id=patient_id, role='patient')
        therapist = User.objects.get(id=therapist_id, role='therapist')

        patient.therapist = therapist
        patient.save()

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



