"""
Admin configuration for Student model.
Features:
- Search by Student ID, first name, last name, email
- Filter by Wilaya and Specialty
- CSV Export action
- Custom display with timestamps
"""
from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model with search, filters, and export."""

    # Display fields in list view
    list_display = [
        'student_id',
        'full_name',
        'email',
        'phone',
        'wilaya',
        'specialty',
        'bac_average',
        'age',
        'consent',
        'created_at',
    ]

    # Search fields
    search_fields = [
        'student_id',
        'first_name',
        'last_name',
        'email',
        'phone',
    ]

    # Filter sidebar
    list_filter = [
        'wilaya',
        'specialty',
        'consent',
        'created_at',
    ]

    # Ordering
    ordering = ['-created_at']

    # Pagination
    list_per_page = 25

    # Read-only fields (timestamps)
    readonly_fields = ['created_at', 'updated_at']

    # Field groups in detail view
    fieldsets = (
        ('Identification', {
            'fields': ('student_id', 'first_name', 'last_name', 'date_of_birth')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Academic', {
            'fields': ('wilaya', 'specialty', 'bac_average')
        }),
        ('Consent & Timestamps', {
            'fields': ('consent', 'created_at', 'updated_at')
        }),
    )

    # Custom actions
    actions = ['export_as_csv']

    def full_name(self, obj):
        """Display full name in list."""
        return obj.full_name
    full_name.short_description = 'Full Name'

    def age(self, obj):
        """Display calculated age in list."""
        return obj.age
    age.short_description = 'Age'

    def export_as_csv(self, request, queryset):
        """
        Export selected students as CSV file.
        Includes all fields plus timestamps.
        """
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=students_export.csv'

        writer = csv.writer(response)

        # Write header with human-readable names
        headers = [
            'Student ID', 'First Name', 'Last Name', 'Date of Birth',
            'Email', 'Phone', 'Wilaya', 'Specialty',
            'Baccalaureate Average', 'Consent',
            'Created At', 'Updated At'
        ]
        writer.writerow(headers)

        # Write data rows
        for obj in queryset:
            writer.writerow([
                obj.student_id,
                obj.first_name,
                obj.last_name,
                obj.date_of_birth,
                obj.email,
                obj.phone,
                obj.wilaya,
                obj.specialty,
                obj.bac_average,
                'Yes' if obj.consent else 'No',
                obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                obj.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response

    export_as_csv.short_description = 'Export selected students to CSV'

    # Custom admin view for full export (all students)
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                'export/',
                self.admin_site.admin_view(self.export_all_csv),
                name='students_student_export_all',
            ),
        ]
        return custom_urls + urls

    def export_all_csv(self, request):
        """Export ALL students to CSV (not just selected)."""
        queryset = self.get_queryset(request)
        return self.export_as_csv(request, queryset)