"""
URL configuration for students app.
"""
from django.urls import path
from .views import StudentFormView, StudentListView

app_name = 'students'

urlpatterns = [
    path('', StudentFormView.as_view(), name='student_form'),
    path('list/', StudentListView.as_view(), name='student_list'),
]