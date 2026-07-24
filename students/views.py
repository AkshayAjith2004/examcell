from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from departments.models import Branch
from .models import Student
from accounts.views import role_required

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER', 'TEACHER'])
def student_list(request):
    query = request.GET.get('q', '').strip()
    students_query = Student.objects.select_related('user', 'branch', 'branch__department').all()
    
    if query:
        students_query = students_query.filter(
            user__first_name__icontains=query) | students_query.filter(
            user__last_name__icontains=query) | students_query.filter(
            admission_number__icontains=query) | students_query.filter(
            branch__code__icontains=query)
            
    students_query = students_query.order_by('admission_number')
    
    paginator = Paginator(students_query, 10) # 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    branches = Branch.objects.select_related('department').all()
    
    return render(request, 'students/student_list.html', {
        'page_obj': page_obj,
        'branches': branches,
        'query': query,
        'semester_choices': range(1, 9)
    })

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER'])
def student_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        admission_number = request.POST.get('admission_number')
        registration_number = request.POST.get('registration_number', '').strip()
        branch_id = request.POST.get('branch')
        semester = request.POST.get('semester')
        phone = request.POST.get('phone')
        photo = request.FILES.get('photo')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
        elif Student.objects.filter(admission_number=admission_number).exists():
            messages.error(request, f"Admission number '{admission_number}' already exists.")
        else:
            try:
                # 1. Create Django User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # 2. Set profile role
                profile = user.profile
                profile.role = 'STUDENT'
                profile.save()
                
                # 3. Create Student profile
                branch = Branch.objects.get(id=branch_id)
                Student.objects.create(
                    user=user,
                    admission_number=admission_number,
                    registration_number=registration_number or None,
                    branch=branch,
                    semester=int(semester),
                    phone=phone,
                    photo=photo
                )
                messages.success(request, f"Student '{first_name} {last_name}' registered successfully.")
            except Exception as e:
                messages.error(request, f"Error registering student: {str(e)}")
                
    return redirect('student_list')

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER'])
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.user.first_name = request.POST.get('first_name')
        student.user.last_name = request.POST.get('last_name')
        student.user.email = request.POST.get('email')
        student.user.save()
        
        branch_id = request.POST.get('branch')
        student.branch = Branch.objects.get(id=branch_id)
        student.semester = int(request.POST.get('semester'))
        student.phone = request.POST.get('phone')
        student.registration_number = request.POST.get('registration_number', '').strip() or None
        
        if request.FILES.get('photo'):
            student.photo = request.FILES.get('photo')
            
        student.save()
        messages.success(request, "Student details updated successfully.")
        return redirect('student_list')
        
    branches = Branch.objects.all()
    return render(request, 'students/student_edit.html', {
        'student': student,
        'branches': branches,
        'semester_choices': range(1, 9)
    })

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER'])
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    user.delete() # cascades to student profile
    messages.success(request, "Student record deleted successfully.")
    return redirect('student_list')
