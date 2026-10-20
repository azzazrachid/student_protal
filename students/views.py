"""
Views for the students app.
- StudentFormView: Handles student registration form (GET/POST)
- StudentListView: Displays submitted students (optional, for user-facing list)
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from .forms import StudentForm
from .models import Student


class StudentFormView(View):
    """
    Handle student registration form.
    GET: Display empty form
    POST: Validate and save student, show errors or success
    """

    template_name = 'students/student_form.html'

    def get(self, request):
        """Display empty registration form."""
        form = StudentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Process submitted form data."""
        form = StudentForm(request.POST)

        if form.is_valid():
            try:
                # Save student (model save() calls full_clean() for extra validation)
                student = form.save()
                messages.success(
                    request,
                    f'Student {student.student_id} - {student.full_name} registered successfully!'
                )
                # Redirect to clear form (PRG pattern)
                return redirect('student_form')
            except Exception as e:
                messages.error(request, f'Error saving student: {str(e)}')
        else:
            # Form has errors - they will be displayed next to each field
            messages.error(request, 'Please correct the errors below.')

        return render(request, self.template_name, {'form': form})


class StudentListView(ListView):
    """
    Display list of registered students (read-only for users).
    Admin interface at /admin/ provides full management.
    """
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        """Optionally filter by search query."""
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(student_id__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search)
            )
        return queryset


# Import Q for search filtering
from django.db import models