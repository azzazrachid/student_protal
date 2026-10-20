"""
Utility functions for the students app.
Helper functions for data cleaning, formatting, and export.
"""
import csv
from django.http import HttpResponse
from .models import Student


def export_students_csv(queryset):
    """
    Export a queryset of students to CSV.
    Used by admin export action.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_export.csv"'

    writer = csv.writer(response)
    # Write header
    writer.writerow([
        'Student ID', 'First Name', 'Last Name', 'Date of Birth',
        'Email', 'Phone', 'Wilaya', 'Specialty',
        'Baccalaureate Average', 'Consent',
        'Created At', 'Updated At'
    ])

    # Write data rows
    for student in queryset:
        writer.writerow([
            student.student_id,
            student.first_name,
            student.last_name,
            student.date_of_birth,
            student.email,
            student.phone,
            student.wilaya,
            student.specialty,
            student.bac_average,
            'Yes' if student.consent else 'No',
            student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            student.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


def get_student_statistics():
    """
    Get basic statistics about students.
    Useful for dashboard/admin overview.
    """
    total = Student.objects.count()
    by_wilaya = Student.objects.values('wilaya').annotate(count=models.Count('wilaya')).order_by('-count')
    by_specialty = Student.objects.values('specialty').annotate(count=models.Count('specialty')).order_by('-count')
    avg_bac = Student.objects.aggregate(avg=models.Avg('bac_average'))['avg']

    return {
        'total_students': total,
        'by_wilaya': list(by_wilaya),
        'by_specialty': list(by_specialty),
        'average_bac': round(avg_bac, 2) if avg_bac else 0,
    }


# Import models here to avoid circular import
from django.db import models