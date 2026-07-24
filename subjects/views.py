from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from departments.models import Department
from teachers.models import Teacher
from .models import Subject
from accounts.views import role_required

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER', 'TEACHER'])
def subject_list(request):
    subjects = Subject.objects.select_related('department', 'faculty', 'faculty__user').all().order_by('subject_code')
    departments = Department.objects.all()
    teachers = Teacher.objects.select_related('user').all()
    
    if request.method == 'POST' and request.user.profile.role in ['ADMIN', 'EXAM_CONTROLLER', 'TEACHER']:
        subject_code = request.POST.get('subject_code').upper()
        subject_name = request.POST.get('subject_name')
        department_id = request.POST.get('department')
        semester = int(request.POST.get('semester'))
        credits = int(request.POST.get('credits'))
        
        if Subject.objects.filter(subject_code=subject_code).exists():
            messages.error(request, f"Subject with code '{subject_code}' already exists.")
        else:
            try:
                dept = Department.objects.get(id=department_id)
                
                Subject.objects.create(
                    subject_code=subject_code,
                    subject_name=subject_name,
                    department=dept,
                    semester=semester,
                    credits=credits
                )
                messages.success(request, f"Subject '{subject_name}' registered successfully.")
            except Exception as e:
                messages.error(request, f"Error registering subject: {str(e)}")
                
        return redirect('subject_list')

    return render(request, 'subjects/subject_list.html', {
        'subjects': subjects,
        'departments': departments,
        'teachers': teachers,
        'semester_choices': range(1, 9)
    })

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER'])
def assign_faculty(request, subject_id):
    if request.method == 'POST':
        subject = get_object_or_404(Subject, id=subject_id)
        faculty_id = request.POST.get('faculty')
        try:
            if faculty_id:
                faculty = Teacher.objects.get(id=faculty_id)
                subject.faculty = faculty
            else:
                subject.faculty = None
            subject.save()
            messages.success(request, f"Faculty assigned successfully to subject '{subject.subject_name}'.")
        except Exception as e:
            messages.error(request, f"Error assigning faculty: {str(e)}")
    return redirect('subject_list')
