from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Count, Sum

from departments.models import Department, Branch, AcademicYear
from classrooms.models import Classroom
from subjects.models import Subject
from students.models import Student
from teachers.models import Teacher
from exams.models import Exam
from timetable.models import Timetable
from seating_app.models import SeatingArrangement
from notifications.models import Notification

def home_view(request):
    departments = Department.objects.all().prefetch_related('branches')
    announcements = Notification.objects.all().order_by('-created_at')[:3]
    
    return render(request, 'core_app/index.html', {
        'departments': departments,
        'announcements': announcements,
    })

@login_required
def dashboard_view(request):
    user = request.user
    role = user.profile.role

    # Common announcement notice board
    notifications = Notification.objects.all().order_by('-created_at')[:5]

    context = {
        'role': role,
        'notifications': notifications,
    }

    if role == 'STUDENT':
        try:
            student = user.student_profile
            allocations = SeatingArrangement.objects.filter(student=student).select_related('classroom', 'exam', 'timetable', 'timetable__subject').order_by('timetable__exam_date', 'timetable__start_time')
            
            # Find timetables for student's branch and semester
            timetable = Timetable.objects.filter(
                subject__department=student.branch.department,
                subject__semester=student.semester
            ).select_related('exam', 'subject').order_by('exam_date', 'start_time')
            
            context.update({
                'student': student,
                'allocations': allocations,
                'timetable': timetable,
            })
        except Student.DoesNotExist:
            context.update({'error_msg': "Student profile not found. Please contact the administrator."})

    elif role == 'TEACHER':
        try:
            teacher = user.teacher_profile
            # Assigned subjects
            subjects = Subject.objects.filter(faculty=teacher).select_related('department')
            upcoming_exams = Timetable.objects.filter(
                subject__faculty=teacher,
                exam_date__gte=date.today()
            ).select_related('exam', 'subject').order_by('exam_date', 'start_time')[:5]
            
            context.update({
                'teacher': teacher,
                'subjects': subjects,
                'upcoming_exams': upcoming_exams,
            })
        except Teacher.DoesNotExist:
            context.update({'error_msg': "Teacher profile not found. Please contact the administrator."})

    elif role in ['ADMIN', 'EXAM_CONTROLLER']:
        # Statistics
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_departments = Department.objects.count()
        total_subjects = Subject.objects.count()
        total_classrooms = Classroom.objects.count()
        total_exams = Exam.objects.count()
        
        # Recent allocations summary
        recent_seating = SeatingArrangement.objects.values(
            'exam__name', 'exam__code', 'timetable__exam_date', 'timetable__session'
        ).annotate(
            student_count=Count('student', distinct=True),
            room_count=Count('classroom', distinct=True)
        ).order_by('-timetable__exam_date')[:5]

        # Upcoming exam timetables
        upcoming_exams = Timetable.objects.filter(
            exam_date__gte=date.today()
        ).select_related('exam', 'subject', 'subject__department').order_by('exam_date', 'start_time')[:5]

        context.update({
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_departments': total_departments,
            'total_subjects': total_subjects,
            'total_classrooms': total_classrooms,
            'total_exams': total_exams,
            'recent_seating': recent_seating,
            'upcoming_exams': upcoming_exams,
        })

    return render(request, 'core_app/dashboard.html', context)
