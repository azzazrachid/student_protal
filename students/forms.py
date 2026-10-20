"""
StudentForm with all data quality rules enforced at the form level.
Provides user-friendly error messages next to each field.
Rules applied:
1. Completeness: All fields required with custom "required" messages
2. Validity: Custom validators + clean methods for format checking
3. Accuracy: DOB validation (not future, age 17-60)
4. Consistency: clean_<field> methods for formatting
5. Uniqueness: Custom clean for friendly duplicate messages
6. Timeliness: Handled by model (auto_now_add, auto_now)
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Student
from .validators import (
    validate_student_id_format,
    validate_algerian_phone,
    validate_bac_average,
    validate_dob_not_future,
    validate_age_range,
    clean_name,
    clean_email,
    clean_phone,
    clean_student_id,
    WILAYA_CHOICES,
    SPECIALTY_CHOICES,
)


class StudentForm(forms.ModelForm):
    """
    Form for student registration with comprehensive validation.
    Each field has custom error messages for clarity.
    """

    # Override fields to customize widgets and error messages
    student_id = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ST202501',
            'pattern': 'ST\\d{6}',
            'title': 'Format: ST + 6 digits (e.g., ST202501)'
        }),
        error_messages={
            'required': 'Student ID is required.',
            'max_length': 'Student ID cannot exceed 8 characters.',
        },
        help_text='Format: ST + 6 digits (e.g., ST202501)'
    )

    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John'
        }),
        error_messages={'required': 'First name is required.'}
    )

    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Doe'
        }),
        error_messages={'required': 'Last name is required.'}
    )

    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        error_messages={
            'required': 'Date of birth is required.',
            'invalid': 'Enter a valid date (YYYY-MM-DD).'
        },
        help_text='Age must be between 17 and 60'
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'john@example.com'
        }),
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.'
        }
    )

    phone = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0555123456',
            'pattern': '(05|06|07)\\d{8}',
            'title': 'Algerian mobile: 05, 06, or 07 + 8 digits'
        }),
        error_messages={
            'required': 'Phone number is required.',
            'max_length': 'Phone number must be 10 digits.',
        },
        help_text='Algerian mobile: 05, 06, or 07 + 8 digits'
    )

    wilaya = forms.ChoiceField(
        choices=[('', 'Select wilaya...')] + WILAYA_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'Wilaya is required.'}
    )

    specialty = forms.ChoiceField(
        choices=[('', 'Select specialty...')] + SPECIALTY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'Specialty is required.'}
    )

    bac_average = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '15.50',
            'step': '0.01',
            'min': '0',
            'max': '20'
        }),
        error_messages={
            'required': 'Baccalaureate average is required.',
            'invalid': 'Enter a valid number (e.g., 15.50).',
            'max_digits': 'Maximum 4 digits allowed.',
            'max_decimal_places': 'Maximum 2 decimal places allowed.',
        },
        help_text='Between 0.00 and 20.00'
    )

    consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'You must consent to proceed.'},
        label='I consent to the processing of my personal data'
    )

    class Meta:
        model = Student
        fields = [
            'student_id', 'first_name', 'last_name', 'date_of_birth',
            'email', 'phone', 'wilaya', 'specialty', 'bac_average', 'consent'
        ]

    # =========================================================================
    # Rule 4: Consistency - Field cleaning methods
    # =========================================================================

    def clean_student_id(self):
        """Clean and validate Student ID format."""
        student_id = self.cleaned_data.get('student_id')
        if student_id:
            # Apply consistency: strip, uppercase
            student_id = clean_student_id(student_id)
            # Validate format
            validate_student_id_format(student_id)
            # Check uniqueness (friendly message)
            if Student.objects.filter(student_id__iexact=student_id).exists():
                raise ValidationError('A student with this Student ID already exists.')
        return student_id

    def clean_first_name(self):
        """Clean first name: capitalize each word."""
        first_name = self.cleaned_data.get('first_name')
        return clean_name(first_name)

    def clean_last_name(self):
        """Clean last name: capitalize each word."""
        last_name = self.cleaned_data.get('last_name')
        return clean_name(last_name)

    def clean_email(self):
        """Clean email: lowercase, check uniqueness."""
        email = self.cleaned_data.get('email')
        if email:
            email = clean_email(email)
            # Check uniqueness (friendly message)
            if Student.objects.filter(email__iexact=email).exists():
                raise ValidationError('A student with this email already exists.')
        return email

    def clean_phone(self):
        """Clean phone: strip spaces, validate format."""
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = clean_phone(phone)
            validate_algerian_phone(phone)
        return phone

    def clean_date_of_birth(self):
        """Validate date of birth: not future, age 17-60."""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            validate_dob_not_future(dob)
            validate_age_range(dob)
        return dob

    def clean_bac_average(self):
        """Validate baccalaureate average: 0-20."""
        avg = self.cleaned_data.get('bac_average')
        if avg is not None:
            validate_bac_average(avg)
        return avg

    def clean_consent(self):
        """Ensure consent is checked."""
        consent = self.cleaned_data.get('consent')
        if not consent:
            raise ValidationError('You must consent to proceed.')
        return consent

    # =========================================================================
    # Rule 1: Completeness - Overall form validation
    # =========================================================================

    def clean(self):
        """
        Final form-wide validation.
        Ensures all required fields are present (completeness check).
        """
        cleaned_data = super().clean()

        # Check for any missing required fields (extra safety)
        required_fields = [
            'student_id', 'first_name', 'last_name', 'date_of_birth',
            'email', 'phone', 'wilaya', 'specialty', 'bac_average', 'consent'
        ]

        for field in required_fields:
            if not cleaned_data.get(field):
                # Add error to specific field if not already there
                if field not in self.errors:
                    self.add_error(field, 'This field is required.')

        return cleaned_data