from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, Branch, AcademicYear
from accounts.views import role_required

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER'])
def department_list(request):
    departments = Department.objects.all().order_by('code')
    academic_years = AcademicYear.objects.all().order_by('-name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_department':
            name = request.POST.get('name')
            code = request.POST.get('code').upper()
            
            if Department.objects.filter(code=code).exists():
                messages.error(request, f"Department code '{code}' already exists.")
            else:
                Department.objects.create(name=name, code=code)
                messages.success(request, f"Department '{name}' added successfully.")
                
        elif action == 'add_academic_year':
            name = request.POST.get('name')
            is_active = request.POST.get('is_active') == 'on'
            
            if AcademicYear.objects.filter(name=name).exists():
                messages.error(request, f"Academic year '{name}' already exists.")
            else:
                AcademicYear.objects.create(name=name, is_active=is_active)
                messages.success(request, f"Academic year '{name}' added successfully.")
                
        return redirect('department_list')

    return render(request, 'departments/department_list.html', {
        'departments': departments,
        'academic_years': academic_years,
    })

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER'])
def branch_list(request):
    branches = Branch.objects.select_related('department').all().order_by('department__code', 'code')
    departments = Department.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code').upper()
        department_id = request.POST.get('department')
        
        try:
            dept = Department.objects.get(id=department_id)
            if Branch.objects.filter(code=code, department=dept).exists():
                messages.error(request, f"Branch code '{code}' already exists in department '{dept.code}'.")
            else:
                Branch.objects.create(name=name, code=code, department=dept)
                messages.success(request, f"Branch '{name}' added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding branch: {str(e)}")
            
        return redirect('branch_list')

    return render(request, 'departments/branch_list.html', {
        'branches': branches,
        'departments': departments,
    })
