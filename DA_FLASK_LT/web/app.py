from flask import Flask, render_template, request, redirect, url_for, session
from models import Database
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = Database()

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        user = db.get_user_by_email_and_password(email, password)
        if user:
            session['loggedin'] = True
            session['userid'] = user[0]
            session['name'] = user[1]
            session['email'] = user[3]
            session['role'] = user[6]
            message = 'Logged in successfully!'
            return redirect(url_for('dashboard'))
        else:
            message = 'Please enter correct email/password!'
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        return render_template("dashboard.html")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        mobile = request.form['mobile']
        user_type = request.form['type']

        if password != confirm_password:
            message = 'Passwords do not match!'
        else:
            if db.get_user_by_email_and_password(email, password):
                message = 'Email is already registered!'
            else:
                hashed_password = password
                
                db.create_user(first_name, last_name, email, hashed_password, mobile, user_type)
                message = 'Registration successful! Please log in.'
                return redirect(url_for('login'))
    
    return render_template('register.html', message=message)

# ########################### TEACHER SECTION ##################################
@app.route("/teacher", methods=['GET', 'POST'])
def teacher():
    if 'loggedin' in session:
        teachers = db.get_all_teachers()
        subjects = db.get_all_subjects()
        return render_template("teacher.html", teachers=teachers, subjects=subjects)
    return redirect(url_for('login'))

@app.route("/edit_teacher", methods=['GET'])
def edit_teacher():
    if 'loggedin' in session:
        teacher_id = request.args.get('teacher_id')
        
        teacher = db.get_teacher_by_id(teacher_id)
        
        if teacher:
            teacher_info = teacher[0]
            
            subjects = db.get_all_subjects()
            
            return render_template("edit_teacher.html", teacher=teacher_info, subjects=subjects)
        else:
            return "Teacher not found", 404
    
    return redirect(url_for('login'))


@app.route("/save_teacher", methods=['POST'])
def save_teacher():
    if 'loggedin' in session:
        if request.method == 'POST' and 'teacher_name' in request.form and 'specialization' in request.form:
            teacher_name = request.form['teacher_name']
            specialization = request.form['specialization']
            action = request.form['action']
            
            if action == 'updateTeacher':
                teacher_id = request.form['teacherid']
                db.save_teacher(teacher_name, specialization, teacher_id)
            else:
                db.save_teacher(teacher_name, specialization)
                
            return redirect(url_for('teacher'))

        elif request.method == 'POST':
            msg = 'Please fill out the form fields!'
            return redirect(url_for('teacher'))

    return redirect(url_for('login'))

@app.route("/delete_teacher", methods=['GET'])
def delete_teacher():
    if 'loggedin' in session:
        teacher_id = request.args.get('teacher_id')
        db.delete_teacher(teacher_id)
        return redirect(url_for('teacher'))
    return redirect(url_for('login'))

########################### SUBJECT ##################################

@app.route("/subject", methods=['GET', 'POST'])
def subject():
    if 'loggedin' in session:
        subjects = db.get_all_subjects()
        return render_template("subject.html", subjects = subjects)
    return redirect(url_for('login'))

@app.route("/edit_subject", methods=['GET'])
def edit_subject():
    if 'loggedin' in session:
        subject_id = request.args.get('subject_id')

        subject = db.get_subject_by_id(subject_id)

        if subject:
            subject_info = subject[0]
            return render_template("edit_subject.html", subject=subject_info)
        else:
            return "Subject not found", 404
    
    return redirect(url_for('login'))


@app.route("/save_subject", methods=['POST'])
def save_subject():
    if 'loggedin' in session:
        
        if request.method == 'POST' and 'subject' in request.form and 's_type' in request.form and 'code' in request.form:
            subject = request.form['subject']
            s_type = request.form['s_type']
            code = request.form['code']
            action = request.form['action']
            
            if action == 'updateSubject':
                subject_id = request.form['subjectid']
                db.save_subject(subject, s_type, code, subject_id)
            else:
                db.save_subject(subject, s_type, code)
            return redirect(url_for('subject'))
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'
        return redirect(url_for('subject'))
    return redirect(url_for('login'))

@app.route("/delete_subject", methods=['GET'])
def delete_subject():
    if 'loggedin' in session:
        subject_id = request.args.get('subject_id')
        db.delete_subject(subject_id)
        return redirect(url_for('subject'))
    return redirect(url_for('login'))

################################ Classes  #######################################

@app.route("/classes", methods=['GET', 'POST'])
def classes():
    if 'loggedin' in session:
        
        classes = db.get_all_classes()
        sections = db.get_all_sections()
        teachers = db.get_all_teachers()
        
        return render_template("class.html", classes=classes, sections=sections, teachers=teachers)
    
    return redirect(url_for('login'))

@app.route("/edit_class", methods=['GET'])
def edit_class():
    if 'loggedin' in session:
        class_id = request.args.get('class_id')

        class_data = db.get_class_by_id(class_id)
        
        if class_data:
            class_info = class_data[0]
            
            sections = db.get_all_sections()
            teachers = db.get_all_teachers()
            
            return render_template("edit_class.html", class_data=class_info, sections=sections, teachers=teachers)
        else:
            return "Class not found", 404
    
    return redirect(url_for('login'))

@app.route("/save_class", methods=['POST'])
def save_class():
    if 'loggedin' in session:
        
        if request.method == 'POST' and 'cname' in request.form and 'sectionid' in request.form and 'teacherid' in request.form:
            cname = request.form['cname']
            sectionid = request.form['sectionid']
            teacherid = request.form['teacherid']
            action = request.form['action']
            
            if action == 'updateClass':
                class_id = request.form['classid']
                db.save_class(cname, sectionid, teacherid, class_id)
            else:
                db.save_class(cname, sectionid, teacherid)
            
            return redirect(url_for('classes'))
        
        elif request.method == 'POST':
            msg = 'Please fill out the form fields!'
            return redirect(url_for('classes'))
    
    return redirect(url_for('login'))


@app.route("/delete_class", methods=['GET'])
def delete_class():
    if 'loggedin' in session:
        class_id = request.args.get('class_id')

        db.delete_class(class_id)
        
        return redirect(url_for('classes'))
    
    return redirect(url_for('login'))

########################### SECTIONS ##################################

@app.route("/sections", methods=['GET', 'POST'])
def sections():
    if 'loggedin' in session:
        
        sections = db.get_all_sections()
        
        return render_template("sections.html", sections=sections)
    return redirect(url_for('login'))

@app.route("/edit_sections", methods=['GET'])
def edit_sections():
    if 'loggedin' in session:
        section_id = request.args.get('section_id')
        
        section = db.get_section_by_id(section_id)

        if section:
            section_info = section[0]
            return render_template("edit_section.html", section=section_info)
        else:
            return "Subject not found", 404
    return redirect(url_for('login'))

@app.route("/save_sections", methods=['POST'])
def save_sections():
    if 'loggedin' in session:
        
        if 'section_name' in request.form:
            section_name = request.form['section_name']
            action = request.form['action']
            
            if action == 'updateSection':
                section_id = request.form['sectionid']
                db.save_section(section_name, section_id)
            else:
                db.save_section(section_name)
            return redirect(url_for('sections'))
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'
        return redirect(url_for('sections'))
    return redirect(url_for('login'))


@app.route("/delete_sections", methods=['GET'])
def delete_sections():
    if 'loggedin' in session:
        section_id = request.args.get('section_id')

        db.delete_section(section_id)
        
        return redirect(url_for('sections'))
    return redirect(url_for('login'))

########################### STUDENTS ##################################

@app.route("/student", methods=['GET', 'POST'])
def student():
    if 'loggedin' in session:

        students = db.get_all_students()
        classes = db.get_all_classes()
        sections = db.get_all_sections()
        
        return render_template("student.html", students=students, classes=classes, sections=sections)
    return redirect(url_for('login'))

@app.route("/edit_student", methods=['GET'])
def edit_student():
    if 'loggedin' in session:
        student_id = request.args.get('student_id')
        
        student = db.get_student_by_id(student_id)
        
        classes = db.get_all_classes()
        sections = db.get_all_sections()


        if student:
            return render_template("edit_student.html", student=student, classes=classes, sections=sections)
        else:
            return "Student not found", 404
    return redirect(url_for('login'))


@app.route("/save_student", methods=['POST'])
def save_student():
    if 'loggedin' in session:
        
        if request.method == 'POST':
            student_data = {
                'name': request.form['name'],
                'gender': request.form['gender'],
                'dob': request.form['dob'],
                'mobile': request.form['mobile'],
                'email': request.form['email'],
                'current_address': request.form['current_address'],
                'class_id': request.form['class_id'],
                'section_id': request.form['section_id'],
                'stream': request.form.get('stream'),  
                'admission_date': request.form['admission_date'],
                'academic_year': request.form['academic_year']
            }
            action = request.form['action']
            
            if action == 'updateStudent':
                student_id = request.form['student_id']
                db.save_student(student_data, student_id)
            else:
                db.save_student(student_data)
            
            return redirect(url_for('student'))
        
        return redirect(url_for('student'))
    return redirect(url_for('login'))

@app.route("/delete_student", methods=['GET'])
def delete_student():
    if 'loggedin' in session:
        student_id = request.args.get('student_id')

        db.delete_student(student_id)
        
        return redirect(url_for('student'))
    return redirect(url_for('login'))

# @app.route("/student", methods=['GET', 'POST'])
# def student():
#     if 'loggedin' in session:
#         # Use db to fetch student data
#         students = db.get_all_students()
#         classes = db.get_all_classes()
#         sections = db.get_all_sections()
#         return render_template("student.html", students=students, classes=classes, sections=sections)
#     return redirect(url_for('login'))

# @app.route("/save_student", methods=['GET', 'POST'])
# def save_student():
#     if 'loggedin' in session:
#         if request.method == 'POST' and 'admission_no' in request.form:
#             admission_no = request.form['admission_no']
#             roll_no = request.form['roll_no']
#             name = request.form['name']
#             photo = request.form['photo']
#             class_id = request.form['class_id']
#             section_id = request.form['section_id']
#             student_id = request.form.get('student_id')
            
#             # Use db instead of data to call save_student
#             db.save_student(admission_no, roll_no, name, photo, class_id, section_id, student_id)
#             return redirect(url_for('student'))
#     return redirect(url_for('login'))

# @app.route("/delete_student", methods=['GET'])
# def delete_student():
#     if 'loggedin' in session:
#         student_id = request.args.get('student_id')
#         # Use db instead of data to call delete_student
#         db.delete_student(student_id)
#         return redirect(url_for('student'))
#     return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
    