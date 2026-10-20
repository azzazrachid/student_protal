"""
Student model with all data quality rules enforced at the database level.
Rules applied:
1. Completeness: All fields required (blank=False, null=False)
2. Validity: Custom validators for Student ID, email, phone, average
3. Accuracy: Custom validators for DOB (not future, age 17-60)
4. Consistency: Clean methods + choices for Wilaya/Specialty
5. Uniqueness: unique=True on student_id and email
6. Timeliness: auto_now_add (created_at), auto_now (updated_at)
"""
from django.db import models
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator
from .validators import (
    validate_student_id_format,
    validate_algerian_phone,
    validate_bac_average,
    validate_dob_not_future,
    validate_age_range,
    WILAYA_CHOICES,
    SPECIALTY_CHOICES,
)


class Student(models.Model):
    """
    Student model representing a student in the information platform.
    All data quality rules are enforced at both model and form level.
    """

    # Rule 1 & 2: Student ID - required, unique, format ST + 6 digits
    student_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[validate_student_id_format],
        help_text='Format: ST + 6 digits (e.g., ST202501)',
        error_messages={
            'unique': 'A student with this Student ID already exists.',
            'blank': 'Student ID is required.',
        }
    )

    # Rule 1 & 4: First name - required, cleaned (capitalized)
    first_name = models.CharField(
        max_length=100,
        help_text='First name (will be capitalized)',
        error_messages={'blank': 'First name is required.'}
    )

    # Rule 1 & 4: Last name - required, cleaned (capitalized)
    last_name = models.CharField(
        max_length=100,
        help_text='Last name (will be capitalized)',
        error_messages={'blank': 'Last name is required.'}
    )

    # Rule 1 & 3: Date of birth - required, not future, age 17-60
    date_of_birth = models.DateField(
        validators=[validate_dob_not_future, validate_age_range],
        help_text='Date of birth (age must be 17-60)',
        error_messages={'blank': 'Date of birth is required.'}
    )

    # Rule 1, 2 & 4: Email - required, unique, valid format, lowercase
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message='Enter a valid email address.')],
        help_text='Email address (will be converted to lowercase)',
        error_messages={
            'unique': 'A student with this email already exists.',
            'blank': 'Email is required.',
        }
    )

    # Rule 1, 2 & 4: Phone - required, Algerian mobile format (05/06/07 + 8 digits)
    phone = models.CharField(
        max_length=10,
        validators=[validate_algerian_phone],
        help_text='Algerian mobile: 05, 06, or 07 + 8 digits',
        error_messages={'blank': 'Phone number is required.'}
    )

    # Rule 1 & 4: Wilaya - required, from fixed list
    wilaya = models.CharField(
        max_length=50,
        choices=WILAYA_CHOICES,
        help_text='Select wilaya from the list',
        error_messages={'blank': 'Wilaya is required.'}
    )

    # Rule 1 & 4: Specialty - required, from fixed list
    specialty = models.CharField(
        max_length=50,
        choices=SPECIALTY_CHOICES,
        help_text='Select specialty from the list',
        error_messages={'blank': 'Specialty is required.'}
    )

    # Rule 1 & 2: Baccalaureate average - required, 0-20
    bac_average = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20), validate_bac_average],
        help_text='Baccalaureate average (0.00 to 20.00)',
        error_messages={'blank': 'Baccalaureate average is required.'}
    )

    # Rule 1: Consent - required checkbox
    consent = models.BooleanField(
        default=False,
        help_text='I consent to the processing of my personal data',
        error_messages={'required': 'You must consent to proceed.'}
    )

    # Rule 6: Timeliness - Automatic timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text='Record creation timestamp')
    updated_at = models.DateTimeField(auto_now=True, help_text='Last update timestamp')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f'{self.student_id} - {self.first_name} {self.last_name}'

    def clean(self):
        """
        Model-level cleaning for consistency (Rule 4).
        Called during model validation (full_clean).
        """
        from .validators import clean_name, clean_email, clean_phone, clean_student_id
        super().clean()

        # Apply consistency rules
        if self.first_name:
            self.first_name = clean_name(self.first_name)
        if self.last_name:
            self.last_name = clean_name(self.last_name)
        if self.email:
            self.email = clean_email(self.email)
        if self.phone:
            self.phone = clean_phone(self.phone)
        if self.student_id:
            self.student_id = clean_student_id(self.student_id)

    def save(self, *args, **kwargs):
        """
        Override save to ensure clean() is called.
        This enforces consistency rules (Rule 4) on every save.
        """
        self.full_clean()  # Runs all validators + clean()
        super().save(*args, **kwargs)

    @property
    def age(self):
        """Calculate current age from date of birth."""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def full_name(self):
        """Return full name."""
        return f'{self.first_name} {self.last_name}'