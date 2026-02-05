import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_123')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# --- MOCK DATABASE ---
# Structured with levels to match your Student.html logic
students = {
    "2024/001": {
        "name": "Alice Johnson", 
        "pw": "123", 
        "level": "200L", 
        "dept": "Computer Science",
        "results": {
            "100L": [{"course": "CSC101", "units": 3, "score": 75.0, "point": 5.0, "grade": "A"}]
        }
    }
}

def calculate_grade(score):
    if score >= 70: return 5.0, "A"
    elif score >= 60: return 4.0, "B"
    elif score >= 50: return 3.0, "C"
    elif score >= 45: return 2.0, "D"
    elif score >= 40: return 1.0, "E"
    else: return 0.0, "F"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form.get('role')
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
    if session.get('user') != 'admin': return redirect(url_for('home'))
    return render_template('admin.html', student_list=students)

@app.route('/student_dashboard')
def student_dashboard():
    username = session.get('user')
    if not username or username == 'admin': return redirect(url_for('home'))
    
    student_data = students.get(username)
    
    # Logic to calculate CGPA and prepare data for the Chart
    total_points = 0
    total_units = 0
    level_gpas = []
    levels = []

    for level, courses in student_data['results'].items():
        levels.append(level)
        l_points = sum(c['point'] * c['units'] for c in courses)
        l_units = sum(c['units'] for c in courses)
        total_points += l_points
        total_units += l_units
        level_gpas.append(round(l_points / l_units, 2) if l_units > 0 else 0)

    cgpa = round(total_points / total_units, 2) if total_units > 0 else 0.0
    
    # Use 'Student.html' (matching your exact filename)
    return render_template('Student.html', data=student_data, cgpa=cgpa, levels=levels, level_gpas=level_gpas)

@app.route('/add_student', methods=['POST'])
def add_student():
    if session.get('user') == 'admin':
        m = request.form.get('matric').upper()
        students[m] = {
            "name": request.form.get('name'),
            "pw": "123",
            "level": request.form.get('level'),
            "dept": request.form.get('dept'),
            "results": {}
        }
        flash("Student Registered!")
    return redirect(url_for('admin_dashboard'))

@app.route('/upload_grade', methods=['POST'])
def upload_grade():
    if session.get('user') == 'admin':
        m = request.form.get('matric').upper()
        lvl = request.form.get('target_level')
        if m in students:
            score = float(request.form.get('score'))
            p, g = calculate_grade(score)
            if lvl not in students[m]['results']: students[m]['results'][lvl] = []
            students[m]['results'][lvl].append({
                "course": request.form.get('course').upper(),
                "units": int(request.form.get('units')),
                "score": score, "point": p, "grade": g
            })
            flash("Result Uploaded!")
    return redirect(url_for('admin_dashboard'))

@app.route('/manage/<path:matric>')
def manage_student(matric):
    if session.get('user') == 'admin' and matric in students:
        return render_template('manage_student.html', matric=matric, info=students[matric])
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
