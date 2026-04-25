from django.shortcuts import render

# Create your views here.
def home_page(request):
    return render(request,"home.html")

def therapist_dashboard(request):
    return render(request, "therapist_dashboard.html")