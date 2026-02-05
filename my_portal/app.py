import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

# --- CONFIGURATION ---
# These pull from your Render Environment Variables
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_123')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# --- MOCK DATABASE ---
# Re-structured to ensure the student login has a place to go
students = {
    "2024/001": {
        "name": "Alice Johnson", 
        "pw": "123", 
        "level": "200L", 
        "dept": "Computer Science",
        "results": [] # List of dicts: {'course': 'CSC101', 'units': 3, 'score': 75.0, 'point': 5.0, 'grade': 'A'}
    }
}

# --- GRADE CALCULATION LOGIC ---
def calculate_grade(score):
    if score >= 70: return 5.0, "A"
    elif score >= 60: return 4.0, "B"
    elif score >= 50: return 3.0, "C"
    elif score >= 45: return 2.0, "D"
    elif score >= 40: return 1.0, "E"
    else: return 0.0, "F"

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form.get('role')
    # .strip().upper() handles accidental spaces or lowercase input
    username = request.form.get('username', '').strip().upper()
    password = request.form.get('password', '').strip()

    if role == 'admin' and password == ADMIN_PASSWORD:
        session['user'] = 'admin'
        return redirect(url_for('admin_dashboard'))
    
    elif username in students and students[username]['pw'] == password:
        session['user'] = username
        return redirect(url_for('student_dashboard'))
    
    flash("Invalid Credentials. Please try again.")
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('user') != 'admin': 
        return redirect(url_for('home'))
    return render_template('admin.html', student_list=students)

@app.route('/student_dashboard')
def student_dashboard():
    # Only allow logged-in students
    username = session.get('user')
    if not username or username == 'admin': 
        return redirect(url_for('home'))
    
    student_data = students.get(username)
    # Calculate CGPA for the student
    total_points = sum(r['point'] * r['units'] for r in student_data['results'])
    total_units = sum(r['units'] for r in student_data['results'])
    cgpa = round(total_points / total_units, 2) if total_units > 0 else 0.0
    
    return render_template('student_portal.html', info=student_data, cgpa=cgpa)

@app.route('/manage/<path:matric>')
def manage_student(matric):
    if session.get('user') != 'admin': 
        return redirect(url_for('home'))
    
    if matric in students:
        return render_template('manage_student.html', matric=matric, info=students[matric])
    
    flash("Student not found.")
    return redirect(url_for('admin_dashboard'))

@app.route('/add_result', methods=['POST'])
def add_result_logic():
    if session.get('user') != 'admin': 
        return redirect(url_for('home'))
    
    matric = request.form.get('matric')
    if matric in students:
        course = request.form.get('course').upper()
        units = int(request.form.get('units'))
        score = float(request.form.get('score'))
        point, grade = calculate_grade(score)
        
        result_entry = {
            "course": course,
            "units": units,
            "score": score,
            "point": point,
            "grade": grade
        }
        students[matric]['results'].append(result_entry)
        flash(f"Result added for {course}")
        
    return redirect(url_for('manage_student', matric=matric))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- PRODUCTION START ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # debug=False is the most important part to avoid the "Interactive PIN" screen
    app.run(host='0.0.0.0', port=port, debug=False)
