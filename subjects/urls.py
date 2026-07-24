from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('assign-faculty/<int:subject_id>/', views.assign_faculty, name='assign_faculty'),
]
