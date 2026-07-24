from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from exams.models import Exam
from subjects.models import Subject
from departments.models import Department
from .models import Timetable
from accounts.views import role_required

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER', 'TEACHER'])
def timetable_list(request):
    entries = Timetable.objects.select_related('exam', 'subject', 'subject__department').all().order_by('exam_date', 'start_time')
    exams = Exam.objects.filter(is_active=True)
    subjects = Subject.objects.all().select_related('department')
    departments = Department.objects.all().order_by('code')
    
    if request.method == 'POST' and request.user.profile.role in ['ADMIN', 'EXAM_CONTROLLER']:
        exam_id = request.POST.get('exam')
        subject_id = request.POST.get('subject')
        exam_date_str = request.POST.get('exam_date')
        session = request.POST.get('session')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        attachment = request.FILES.get('attachment')
        
        try:
            exam = Exam.objects.get(id=exam_id)
            subject = Subject.objects.get(id=subject_id)
            
            Timetable.objects.create(
                exam=exam,
                subject=subject,
                exam_date=exam_date_str,
                session=session,
                start_time=start_time_str,
                end_time=end_time_str,
                attachment=attachment
            )
            messages.success(request, f"Scheduled exam slot for '{subject.subject_name}' successfully.")
        except Exception as e:
            messages.error(request, f"Error scheduling exam slot: {str(e)}")
            
        return redirect('timetable_list')
        
    return render(request, 'timetable/timetable_list.html', {
        'entries': entries,
        'exams': exams,
        'subjects': subjects,
        'departments': departments,
    })

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER'])
def timetable_delete(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)
    subject_name = entry.subject.subject_name
    entry.delete()
    messages.success(request, f"Scheduled exam slot for '{subject_name}' deleted successfully.")
    return redirect('timetable_list')

