# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Patient, TherapyPlan, Session, Report,SupervisorFeedback
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors

@login_required
def add_patient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = int(request.POST.get('age'))
        if age < 0 or age > 120:
            return HttpResponse("Invalid age") 
        speech_issue = request.POST.get('speech_issue')
        contact = request.POST.get('contact')

        Patient.objects.create(
            name=name,
            age=age,
            speech_issue=speech_issue,
            contact=contact,
            assigned_therapist=request.user
        )

        return redirect('therapist_dashboard')

    return render(request, 'therapy/add_patient.html')

def patient_list(request):
    patients = Patient.objects.filter(assigned_therapist=request.user)
    return render(request, 'therapy/patient_list.html', {'patients': patients})

def create_plan(request):
    patients = Patient.objects.filter(assigned_therapist=request.user)

    if request.method == 'POST':

        patient_id = request.POST.get('patient')
        if not patient_id:
            return HttpResponse("Please select a patient")
        patient_id = int(patient_id)
        exercises = request.POST.get('exercises')
        goals = request.POST.get('goals')
        duration = int(request.POST.get('duration'))
        
        if TherapyPlan.objects.filter(
            patient_id=patient_id,
            is_submitted=False,
            is_approved=False
        ).exists():
            return HttpResponse("❌ You already have a pending plan for this patient")

        # ✅ Validation
        if duration <= 0:
            return render(request, 'therapy/create_plan.html', {
                'patients': patients,
                'error': 'Duration must be positive'
            })
        

        TherapyPlan.objects.create(
            patient_id=patient_id,
            therapist=request.user,
            exercises=exercises,
            goals=goals,
            duration=duration
        )

        return redirect('therapist_dashboard')

    return render(request, 'therapy/create_plan.html', {'patients': patients})

def plan_list(request):
    plans = TherapyPlan.objects.filter(therapist=request.user)
    return render(request, 'therapy/plan_list.html', {'plans': plans})

def submit_plan(request, id):
    plan = TherapyPlan.objects.get(id=id)
    plan.is_submitted = True
    plan.save()

    return redirect('plan_list')

def approve_plan(request, id):
    plan = TherapyPlan.objects.get(id=id)
    plan.is_approved = True
    plan.save()

    return redirect('supervisor_dashboard')

def add_session(request, plan_id):
    plan = TherapyPlan.objects.get(id=plan_id)

    # 🚨 Only approved plans allowed
    if not plan.is_approved:
        return redirect('plan_list')

    MAX_SESSIONS = 10  # fixed rule

    sessions = Session.objects.filter(plan=plan)
    session_count = sessions.count()

    # 🚨 stop if limit reached
    if session_count >= MAX_SESSIONS:
        return redirect('plan_list')

    if request.method == 'POST':
        date = request.POST.get('date')
        progress = request.POST.get('progress')
        notes = request.POST.get('notes')

        # ✅ create session
        Session.objects.create(
            plan=plan,
            session_number=session_count + 1,
            date=date,
            progress=progress,
            notes=notes
        )

        # update count AFTER insertion (IMPORTANT FIX)
        session_count += 1

        # ✅ GENERATE REPORT WHEN LAST SESSION IS DONE
        if session_count == MAX_SESSIONS:

            # safety check to avoid duplicate reports
            if not Report.objects.filter(plan=plan).exists():

                all_sessions = Session.objects.filter(plan=plan).order_by('session_number')

                summary = "Therapy Report:\n\n"
                for s in all_sessions:
                    summary += (
                        f"Session {s.session_number}\n"
                        f"Progress: {s.progress}\n"
                        f"Notes: {s.notes}\n\n"
                    )

                Report.objects.create(
                    plan=plan,
                    summary=summary
                )

        return redirect('view_sessions', plan_id=plan.id)

    return render(request, 'therapy/add_session.html', {'plan': plan})

def view_sessions(request, plan_id):
    plan = TherapyPlan.objects.get(id=plan_id)
    sessions = Session.objects.filter(plan=plan)
    count = sessions.count()
    MAX_SESSIONS = 10

    return render(request, 'therapy/session_list.html', {
        'plan': plan,
        'sessions': sessions,
        'max_sessions': MAX_SESSIONS
    })

def edit_patient(request, id):
    patient = Patient.objects.get(id=id)

    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.age = request.POST.get('age')
        patient.speech_issue = request.POST.get('speech_issue')
        patient.contact = request.POST.get('contact')
        patient.save()

        return redirect('patient_list')

    return render(request, 'therapy/edit_patient.html', {'patient': patient})

def delete_patient(request, id):
    patient = Patient.objects.get(id=id)
    patient.delete()
    return redirect('patient_list')


def generate_report(request, plan_id):
    plan = TherapyPlan.objects.get(id=plan_id)
    sessions = Session.objects.filter(plan=plan)

    # CONDITION: minimum 10 sessions
    if sessions.count() < 10:
        return HttpResponse("❌ Need at least 10 sessions to generate report")

    # create report
    Report.objects.create(
        plan=plan,
        summary="Patient is improving well based on sessions."
    )

    return redirect('plan_list')

def report_list(request):
    reports = Report.objects.all()
    return render(request, 'therapy/report_list.html', {'reports': reports})

def approve_report(request, id):
    report = Report.objects.get(id=id)
    report.status = "Approved"
    report.save()

    return redirect('report_list')

def view_report(request, plan_id):
    plan = TherapyPlan.objects.get(id=plan_id)
    report = Report.objects.filter(plan=plan).first()

    if not report:
        return render(request, 'therapy/view_report.html', {
            'plan': plan,
            'report': None
        })

    return render(request, 'therapy/view_report.html', {
        'report': report
    })

def download_report_pdf(request, report_id):
    report = Report.objects.get(id=report_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="therapy_report_{report.id}.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Speech Therapy Report")

    p.setFont("Helvetica", 12)
    p.drawString(50, 750, f"Patient: {report.plan.patient.name}")

    text = p.beginText(50, 720)
    text.textLines("Summary:\n" + report.summary)

    p.drawText(text)
    p.showPage()
    p.save()

    return response

def supervisor_dashboard(request):
    plans = TherapyPlan.objects.all()

    dashboard_data = []

    for plan in plans:
        sessions = Session.objects.filter(plan=plan).count()
        report = Report.objects.filter(plan=plan).first()

        dashboard_data.append({
            'plan': plan,
            'sessions_done': sessions,
            'progress_percent': int((sessions / 10) * 100),
            'report': report
        })

    feedbacks = SupervisorFeedback.objects.all().order_by('-created_at')

    return render(request, 'supervisor_dashboard.html', {
        'dashboard_data': dashboard_data,
        'feedbacks': feedbacks
    })

def add_feedback(request, plan_id):
    plan = TherapyPlan.objects.get(id=plan_id)

    if request.method == "POST":
        feedback_text = request.POST.get("feedback")
        rating = int(request.POST.get("rating"))

        SupervisorFeedback.objects.create(
            plan=plan,
            feedback=feedback_text,
            rating=rating
        )

        return redirect('supervisor_dashboard')

    return render(request, 'therapy/add_feedback.html', {'plan': plan})

def edit_feedback(request, feedback_id):
    feedback = SupervisorFeedback.objects.get(id=feedback_id)

    if request.method == "POST":
        feedback_text = request.POST.get("feedback")

        feedback.feedback = feedback_text
        feedback.rating = int(request.POST.get("rating"))
        feedback.save()

        return redirect('supervisor_dashboard')

    return render(request, 'therapy/edit_feedback.html', {
        'feedback': feedback
    })

def delete_feedback(request, feedback_id):
    feedback = SupervisorFeedback.objects.get(id=feedback_id)

    if request.method == "POST":
        feedback.delete()
        return redirect('supervisor_dashboard')

    return render(request, 'therapy/delete_feedback.html', {
        'feedback': feedback
    })

def generate_certificate(request, plan_id):
    from .models import TherapyPlan

    plan = TherapyPlan.objects.get(id=plan_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)

    styles = getSampleStyleSheet()

    content = []

    # 🏆 TITLE
    content.append(Spacer(1, 1*inch))
    content.append(Paragraph(
        "<para align='center'><font size=24 color='blue'><b>CERTIFICATE OF COMPLETION</b></font></para>",
        styles['Normal']
    ))

    content.append(Spacer(1, 0.5*inch))

    # 📄 BODY TEXT
    content.append(Paragraph(
        f"<para align='center'><font size=14>"
        f"This is to certify that"
        f"</font></para>",
        styles['Normal']
    ))

    content.append(Spacer(1, 0.3*inch))

    # 🎯 PATIENT NAME (BIG + BOLD)
    content.append(Paragraph(
        f"<para align='center'><font size=18 color='green'><b>{plan.patient.name}</b></font></para>",
        styles['Normal']
    ))

    content.append(Spacer(1, 0.3*inch))

    content.append(Paragraph(
        "<para align='center'><font size=14>"
        "has successfully completed the Speech Therapy Program."
        "</font></para>",
        styles['Normal']
    ))

    content.append(Spacer(1, 0.5*inch))

    # 📅 DATE
    import datetime
    today = datetime.date.today()

    content.append(Paragraph(
        f"<para align='center'><font size=12>"
        f"Date: {today}"
        "</font></para>",
        styles['Normal']
    ))

    content.append(Spacer(1, 1*inch))

    # ✍ SIGNATURE
    content.append(Paragraph(
        "<para align='center'><font size=12>"
        "_________________________<br/>Supervisor Signature"
        "</font></para>",
        styles['Normal']
    ))

    doc.build(content)

    return response