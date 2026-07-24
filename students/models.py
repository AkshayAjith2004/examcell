from django.db import models
from django.contrib.auth.models import User
from departments.models import Branch

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='students')
    semester = models.PositiveIntegerField()
    phone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='students/photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.admission_number})"
