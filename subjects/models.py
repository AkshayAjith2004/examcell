from django.db import models
from departments.models import Department

class Subject(models.Model):
    subject_code = models.CharField(max_length=50, unique=True)
    subject_name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    semester = models.PositiveIntegerField()
    credits = models.PositiveIntegerField(default=3)
    faculty = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_subjects')

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
