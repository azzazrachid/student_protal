"""
Custom validators for Student model - implementing data quality rules.
Each validator enforces a specific quality rule.
"""
import re
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# ============================================================================
# Rule 2: Validity - Format validators
# ============================================================================

def validate_student_id_format(value):
    """
    Validate Student ID format: ST + 6 digits (e.g., ST202501).
    Rule 2: Validity
    """
    pattern = r'^ST\d{6}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Invalid Student ID format. Must be ST followed by 6 digits (e.g., ST202501).'),
            params={'value': value},
        )


def validate_algerian_phone(value):
    """
    Validate Algerian mobile number: 05, 06, or 07 + 8 digits.
    Rule 2: Validity
    """
    pattern = r'^(05|06|07)\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Invalid Algerian phone number. Must start with 05, 06, or 07 followed by 8 digits.'),
            params={'value': value},
        )


def validate_bac_average(value):
    """
    Validate baccalaureate average is between 0 and 20.
    Rule 2: Validity
    """
    if value < 0 or value > 20:
        raise ValidationError(
            _('Baccalaureate average must be between 0 and 20.'),
            params={'value': value},
        )


# ============================================================================
# Rule 3: Accuracy - Date of birth validators
# ============================================================================

def validate_dob_not_future(value):
    """
    Validate date of birth is not in the future.
    Rule 3: Accuracy
    """
    if value > date.today():
        raise ValidationError(
            _('Date of birth cannot be in the future.'),
            params={'value': value},
        )


def validate_age_range(value):
    """
    Validate age is between 17 and 60.
    Rule 3: Accuracy
    """
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 17 or age > 60:
        raise ValidationError(
            _('Age must be between 17 and 60 years old.'),
            params={'value': value, 'age': age},
        )


# ============================================================================
# Rule 4: Consistency - Cleaning functions (used in form clean_<field> methods)
# ============================================================================

def clean_name(value):
    """
    Clean name: strip extra spaces, capitalize first letter of each word.
    Rule 4: Consistency
    """
    if value:
        return ' '.join(word.capitalize() for word in value.strip().split())
    return value


def clean_email(value):
    """
    Clean email: strip spaces, convert to lowercase.
    Rule 4: Consistency
    """
    if value:
        return value.strip().lower()
    return value


def clean_phone(value):
    """
    Clean phone: strip spaces.
    Rule 4: Consistency
    """
    if value:
        return value.strip()
    return value


def clean_student_id(value):
    """
    Clean student ID: strip spaces, uppercase.
    Rule 4: Consistency
    """
    if value:
        return value.strip().upper()
    return value


# Wilaya choices (58 Algerian wilayas)
WILAYA_CHOICES = [
    ('Adrar', 'Adrar'),
    ('Chlef', 'Chlef'),
    ('Laghouat', 'Laghouat'),
    ('Oum El Bouaghi', 'Oum El Bouaghi'),
    ('Batna', 'Batna'),
    ('Bejaia', 'Bejaia'),
    ('Biskra', 'Biskra'),
    ('Bechar', 'Bechar'),
    ('Blida', 'Blida'),
    ('Bouira', 'Bouira'),
    ('Tamanrasset', 'Tamanrasset'),
    ('Tebessa', 'Tebessa'),
    ('Tlemcen', 'Tlemcen'),
    ('Tiaret', 'Tiaret'),
    ('Tizi Ouzou', 'Tizi Ouzou'),
    ('Algiers', 'Algiers'),
    ('Djelfa', 'Djelfa'),
    ('Jijel', 'Jijel'),
    ('Setif', 'Setif'),
    ('Saida', 'Saida'),
    ('Skikda', 'Skikda'),
    ('Sidi Bel Abbes', 'Sidi Bel Abbes'),
    ('Annaba', 'Annaba'),
    ('Guelma', 'Guelma'),
    ('Constantine', 'Constantine'),
    ('Medea', 'Medea'),
    ('Mostaganem', 'Mostaganem'),
    ('Msila', 'Msila'),
    ('Mascara', 'Mascara'),
    ('Ouargla', 'Ouargla'),
    ('Oran', 'Oran'),
    ('El Bayadh', 'El Bayadh'),
    ('Illizi', 'Illizi'),
    ('Bordj Bou Arreridj', 'Bordj Bou Arreridj'),
    ('Boumerdes', 'Boumerdes'),
    ('El Tarf', 'El Tarf'),
    ('Tindouf', 'Tindouf'),
    ('Tissemsilt', 'Tissemsilt'),
    ('El Oued', 'El Oued'),
    ('Khenchela', 'Khenchela'),
    ('Souk Ahras', 'Souk Ahras'),
    ('Tipaza', 'Tipaza'),
    ('Mila', 'Mila'),
    ('Ain Defla', 'Ain Defla'),
    ('Naama', 'Naama'),
    ('Ain Temouchent', 'Ain Temouchent'),
    ('Ghardaia', 'Ghardaia'),
    ('Relizane', 'Relizane'),
    ('Timimoun', 'Timimoun'),
    ('Bordj Badji Mokhtar', 'Bordj Badji Mokhtar'),
    ('Ouled Djellal', 'Ouled Djellal'),
    ('Beni Abbes', 'Beni Abbes'),
    ('In Salah', 'In Salah'),
    ('In Guezzam', 'In Guezzam'),
    ('Touggourt', 'Touggourt'),
    ('Djanet', 'Djanet'),
    ('El Mghair', 'El Mghair'),
    ('El Meniaa', 'El Meniaa'),
]


# Specialty choices
SPECIALTY_CHOICES = [
    ('Computer Science', 'Computer Science'),
    ('Information Systems', 'Information Systems'),
    ('Data Science', 'Data Science'),
    ('Software Engineering', 'Software Engineering'),
    ('Networks & Security', 'Networks & Security'),
    ('Artificial Intelligence', 'Artificial Intelligence'),
    ('Web Development', 'Web Development'),
    ('Mobile Development', 'Mobile Development'),
    ('Cybersecurity', 'Cybersecurity'),
    ('Cloud Computing', 'Cloud Computing'),
]