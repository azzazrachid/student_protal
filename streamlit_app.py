import streamlit as st
import pandas as pd
import sqlite3
import re
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "db.sqlite3"

WILAYA_CHOICES = [
    'Adrar', 'Chlef', 'Laghouat', 'Oum El Bouaghi', 'Batna', 'Bejaia', 'Biskra',
    'Bechar', 'Blida', 'Bouira', 'Tamanrasset', 'Tebessa', 'Tlemcen', 'Tiaret',
    'Tizi Ouzou', 'Algiers', 'Djelfa', 'Jijel', 'Setif', 'Saida', 'Skikda',
    'Sidi Bel Abbes', 'Annaba', 'Guelma', 'Constantine', 'Medea', 'Mostaganem',
    'Msila', 'Mascara', 'Ouargla', 'Oran', 'El Bayadh', 'Illizi',
    'Bordj Bou Arreridj', 'Boumerdes', 'El Tarf', 'Tindouf', 'Tissemsilt',
    'El Oued', 'Khenchela', 'Souk Ahras', 'Tipaza', 'Mila', 'Ain Defla',
    'Naama', 'Ain Temouchent', 'Ghardaia', 'Relizane', 'Timimoun',
    'Bordj Badji Mokhtar', 'Ouled Djellal', 'Beni Abbes', 'In Salah',
    'In Guezzam', 'Touggourt', 'Djanet', 'El Mghair', 'El Meniaa'
]

SPECIALTY_CHOICES = [
    'Computer Science', 'Information Systems', 'Data Science', 'Software Engineering',
    'Networks & Security', 'Artificial Intelligence', 'Web Development',
    'Mobile Development', 'Cybersecurity', 'Cloud Computing'
]

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students_student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            wilaya TEXT NOT NULL,
            specialty TEXT NOT NULL,
            bac_average REAL NOT NULL,
            consent BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def validate_student_id(value):
    pattern = r'^ST\d{6}$'
    if not re.match(pattern, value):
        raise ValueError('Invalid Student ID format. Must be ST followed by 6 digits (e.g., ST202501).')
    return value.upper().strip()

def validate_phone(value):
    pattern = r'^(05|06|07)\d{8}$'
    if not re.match(pattern, value):
        raise ValueError('Invalid Algerian phone number. Must start with 05, 06, or 07 followed by 8 digits.')
    return value.strip()

def validate_email(value):
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
        raise ValueError('Enter a valid email address.')
    return value.strip().lower()

def validate_bac_average(value):
    if value < 0 or value > 20:
        raise ValueError('Baccalaureate average must be between 0 and 20.')
    return value

def validate_dob(value):
    if value > date.today():
        raise ValueError('Date of birth cannot be in the future.')
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 17 or age > 60:
        raise ValueError(f'Age must be between 17 and 60 years old. Current age: {age}')
    return value

def clean_name(value):
    if value:
        return ' '.join(word.capitalize() for word in value.strip().split())
    return value

def load_students():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM students_student ORDER BY created_at DESC", conn)
    conn.close()
    return df

def add_student(data):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO students_student 
            (student_id, first_name, last_name, date_of_birth, email, phone, wilaya, specialty, bac_average, consent, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['student_id'], data['first_name'], data['last_name'],
            data['date_of_birth'], data['email'], data['phone'],
            data['wilaya'], data['specialty'], data['bac_average'],
            data['consent'], datetime.now().isoformat(), datetime.now().isoformat()
        ))
        conn.commit()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError as e:
        if 'student_id' in str(e):
            return False, "Student ID already exists."
        elif 'email' in str(e):
            return False, "Email already exists."
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def update_student(student_id, data):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE students_student 
            SET first_name=?, last_name=?, date_of_birth=?, email=?, phone=?, wilaya=?, specialty=?, bac_average=?, consent=?, updated_at=?
            WHERE student_id=?
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'],
            data['email'], data['phone'], data['wilaya'], data['specialty'],
            data['bac_average'], data['consent'], datetime.now().isoformat(),
            student_id
        ))
        conn.commit()
        return True, "Student updated successfully!"
    except sqlite3.IntegrityError as e:
        if 'email' in str(e):
            return False, "Email already exists."
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def delete_student(student_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM students_student WHERE student_id=?", (student_id,))
        conn.commit()
        return True, "Student deleted successfully!"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def get_student(student_id):
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM students_student WHERE student_id=?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row

st.set_page_config(page_title="Student Portal", page_icon="🎓", layout="wide")

init_db()

st.title("🎓 Student Portal - Data Quality Platform")
st.markdown("Manage student records with full data quality validation")

tab1, tab2, tab3 = st.tabs(["📋 View Students", "➕ Add Student", "✏️ Edit/Delete"])

with tab1:
    st.subheader("All Students")
    df = load_students()
    
    if df.empty:
        st.info("No students found. Add your first student in the 'Add Student' tab.")
    else:
        display_df = df.copy()
        display_df['age'] = display_df['date_of_birth'].apply(
            lambda x: date.today().year - pd.to_datetime(x).year - 
            ((date.today().month, date.today().day) < (pd.to_datetime(x).month, pd.to_datetime(x).day))
        )
        display_df['consent'] = display_df['consent'].map({1: '✅ Yes', 0: '❌ No'})
        
        st.dataframe(
            display_df[['student_id', 'first_name', 'last_name', 'age', 'email', 'phone', 'wilaya', 'specialty', 'bac_average', 'consent', 'created_at']],
            use_container_width=True,
            hide_index=True
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Students", len(df))
        with col2:
            st.metric("Average BAC Score", f"{df['bac_average'].mean():.2f}")

with tab2:
    st.subheader("Add New Student")
    
    with st.form("add_student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("Student ID *", placeholder="ST202501", help="Format: ST + 6 digits")
            first_name = st.text_input("First Name *", placeholder="Ahmed")
            last_name = st.text_input("Last Name *", placeholder="Benali")
            dob = st.date_input("Date of Birth *", min_value=date(1964, 1, 1), max_value=date.today(), help="Age must be 17-60")
            email = st.text_input("Email *", placeholder="ahmed@example.com")
        
        with col2:
            phone = st.text_input("Phone *", placeholder="0555123456", help="Algerian mobile: 05, 06, or 07 + 8 digits")
            wilaya = st.selectbox("Wilaya *", WILAYA_CHOICES)
            specialty = st.selectbox("Specialty *", SPECIALTY_CHOICES)
            bac_average = st.number_input("BAC Average *", min_value=0.0, max_value=20.0, step=0.01, format="%.2f")
            consent = st.checkbox("I consent to the processing of my personal data *")
        
        submitted = st.form_submit_button("Add Student", type="primary", use_container_width=True)
        
        if submitted:
            errors = []
            try:
                student_id = validate_student_id(student_id)
            except ValueError as e:
                errors.append(f"Student ID: {e}")
            
            try:
                first_name = clean_name(first_name)
                if not first_name:
                    errors.append("First Name is required")
            except:
                errors.append("First Name is required")
            
            try:
                last_name = clean_name(last_name)
                if not last_name:
                    errors.append("Last Name is required")
            except:
                errors.append("Last Name is required")
            
            try:
                validate_dob(dob)
            except ValueError as e:
                errors.append(f"Date of Birth: {e}")
            
            try:
                email = validate_email(email)
            except ValueError as e:
                errors.append(f"Email: {e}")
            
            try:
                phone = validate_phone(phone)
            except ValueError as e:
                errors.append(f"Phone: {e}")
            
            try:
                bac_average = validate_bac_average(bac_average)
            except ValueError as e:
                errors.append(f"BAC Average: {e}")
            
            if not consent:
                errors.append("Consent is required")
            
            if errors:
                for err in errors:
                    st.error(err)
            else:
                data = {
                    'student_id': student_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'date_of_birth': dob.isoformat(),
                    'email': email,
                    'phone': phone,
                    'wilaya': wilaya,
                    'specialty': specialty,
                    'bac_average': bac_average,
                    'consent': consent
                }
                success, msg = add_student(data)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

with tab3:
    st.subheader("Edit or Delete Student")
    df = load_students()
    
    if df.empty:
        st.info("No students to edit.")
    else:
        student_ids = df['student_id'].tolist()
        selected_id = st.selectbox("Select Student", student_ids)
        
        if selected_id:
            student = get_student(selected_id)
            if student:
                _, sid, fn, ln, dob_str, email, phone, wilaya, specialty, bac_avg, consent, created, updated = student
                
                with st.form("edit_student_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text_input("Student ID (read-only)", value=sid, disabled=True)
                        first_name = st.text_input("First Name *", value=fn)
                        last_name = st.text_input("Last Name *", value=ln)
                        dob = st.date_input("Date of Birth *", value=pd.to_datetime(dob_str).date(), min_value=date(1964, 1, 1), max_value=date.today())
                        email = st.text_input("Email *", value=email)
                    
                    with col2:
                        phone = st.text_input("Phone *", value=phone)
                        wilaya = st.selectbox("Wilaya *", WILAYA_CHOICES, index=WILAYA_CHOICES.index(wilaya) if wilaya in WILAYA_CHOICES else 0)
                        specialty = st.selectbox("Specialty *", SPECIALTY_CHOICES, index=SPECIALTY_CHOICES.index(specialty) if specialty in SPECIALTY_CHOICES else 0)
                        bac_average = st.number_input("BAC Average *", min_value=0.0, max_value=20.0, step=0.01, format="%.2f", value=float(bac_avg))
                        consent = st.checkbox("Consent", value=bool(consent))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_btn = st.form_submit_button("Update Student", type="primary", use_container_width=True)
                    with col2:
                        delete_btn = st.form_submit_button("Delete Student", type="secondary", use_container_width=True)
                    
                    if update_btn:
                        errors = []
                        try:
                            first_name = clean_name(first_name)
                            last_name = clean_name(last_name)
                            email = validate_email(email)
                            phone = validate_phone(phone)
                            validate_dob(dob)
                            bac_average = validate_bac_average(bac_average)
                            if not consent:
                                errors.append("Consent is required")
                        except ValueError as e:
                            errors.append(str(e))
                        
                        if errors:
                            for err in errors:
                                st.error(err)
                        else:
                            data = {
                                'first_name': first_name,
                                'last_name': last_name,
                                'date_of_birth': dob.isoformat(),
                                'email': email,
                                'phone': phone,
                                'wilaya': wilaya,
                                'specialty': specialty,
                                'bac_average': bac_average,
                                'consent': consent
                            }
                            success, msg = update_student(sid, data)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    
                    if delete_btn:
                        if st.checkbox("Confirm deletion", key="confirm_delete"):
                            success, msg = delete_student(sid)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

st.markdown("---")
st.caption("Student Portal - Data Quality Enforcement Platform")