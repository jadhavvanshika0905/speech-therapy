from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login

# Create your views here.

def admin_login(request):
    if request=="POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request,username=username,password = password)

        if user is not None:
            if user.is_superuser or user.role=="admin":
                login(request,user)
                return redirect("admin_dashboard")
            else:
                return render(render,"admin_lofin.html",{'error':"user Not Found!! Try again"})
        else:
            return render(render,"admin_login.html",{'error':"Invalid credentials"})
        
    return render(request,'admin_login.html')
