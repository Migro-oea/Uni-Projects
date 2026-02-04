import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

# --- SECURITY CONFIGURATION ---
# This pulls the 'SECRET_KEY' you just set on Render.
# If testing locally, it defaults to 'dev_key'.
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_local_testing')

# Pulls the Admin Password from Render. Defaults to 'admin123' locally.
admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')

# --- MOCK DATABASE ---
students = {
    "2024/001": {
        "name": "Alice Johnson", "pw": "123", "level": "200L", "dept": "Computer Science",
        "results": {"100L": [{"course": "CSC101", "units": 3, "score": 75.0, "point": 5.0, "grade": "A"}]}
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
    username = request.form.get('username').upper()
    password = request.form.get('password')

    if role == 'admin' and password == admin_pass:
        session['user'] = 'admin'
        return redirect(url_for('admin_dashboard'))
    elif username in students and students[username]['pw'] == password:
        session['user'] = username
        return redirect(url_for('student_dashboard'))
    flash("Invalid Credentials")
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('user') != 'admin': return redirect(url_for('home'))
    return render_template('admin.html', student_list=students)

# FIXED PATH FOR PRODUCTION SLASHES
@app.route('/manage/<path:matric>')
def manage_student(matric):
    if session.get('user') != 'admin': return redirect(url_for('home'))
    if matric in students:
        return render_template('manage_student.html', matric=matric, info=students[matric])
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_student/<path:matric>')
def delete_student(matric):
    if session.get('user') == 'admin' and matric in students:
        del students[matric]
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- PRODUCTION ENTRY POINT ---
if __name__ == "__main__":
    # This port logic is required for Render deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
