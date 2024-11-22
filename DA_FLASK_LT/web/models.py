import hashlib
import mysql.connector as mysql
from config import Config

class Database:
    GUIDB = "flaskdb"

    def connect(self):
        conn = mysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
        )
        cursor = conn.cursor()
        return conn, cursor

    def close(self, cursor, conn):
        cursor.close()
        conn.close()

    def createGuiDB(self):
        conn, cursor = self.connect()

        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.GUIDB}")
            conn.commit()
            print(f"Database {self.GUIDB} created successfully")
        except mysql.Error as error:
            print(f"Failed to create database: {error}")
        
        self.close(cursor, conn)
    
    def dropGuiDB(self):
        conn, cursor = self.connect()
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {self.GUIDB}")
            conn.commit()
            print(f"Database {self.GUIDB} dropped successfully")
        except mysql.Error as error:
            print(f"Failed to drop database: {error}")
        self.close(cursor, conn)
    
    def useGuiDB(self, cursor):
        cursor.execute(f"USE {self.GUIDB}")

    def createTables(self):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `classes` (
            `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `name` varchar(40) NOT NULL,
            `section` varchar(255) NOT NULL,
            `teacher_id` int(11) NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `section` (
            `section_id` int(11) NOT NULL AUTO_INCREMENT,
            `section` varchar(255) NOT NULL,
            PRIMARY KEY (`section_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    """)
        
        print("Bảng 'section' đã được tạo hoặc đã tồn tại.")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `students` (
            `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `name` varchar(40) NOT NULL,
            `gender` varchar(40) NOT NULL,
            `dob` varchar(255) NOT NULL,
            `mobile` int(10) UNSIGNED NOT NULL,
            `email` varchar(40) DEFAULT NULL,
            `current_address` varchar(40) DEFAULT NULL,
            `class` int(10) UNSIGNED NOT NULL,
            `section` int(11) NOT NULL,
            `stream` int(10) UNSIGNED DEFAULT NULL,
            `admission_date` varchar(255) NOT NULL,
            `academic_year` int(10) UNSIGNED NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """)
        
        print("Bảng 'students' đã được tạo hoặc đã tồn tại.")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `subjects` (
            `subject_id` int(11) NOT NULL AUTO_INCREMENT,
            `subject` varchar(255) NOT NULL,
            `type` varchar(255) NOT NULL,
            `code` int(11) NOT NULL,
            PRIMARY KEY (`subject_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    """)
        
        print("Bảng 'subjects' đã được tạo hoặc đã tồn tại.")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `teacher` (
            `teacher_id` int(11) NOT NULL AUTO_INCREMENT,
            `teacher` varchar(255) NOT NULL,
            `subject_id` int(11) NOT NULL,
            PRIMARY KEY (`teacher_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    """)
        
        print("Bảng 'teacher' đã được tạo hoặc đã tồn tại.")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `user` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `first_name` varchar(50) NOT NULL,
            `last_name` varchar(50) NOT NULL,
            `email` varchar(50) NOT NULL,
            `password` varchar(255) NOT NULL,
            `mobile` varchar(50) NOT NULL,
            `type` varchar(250) NOT NULL DEFAULT 'general',
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    """)
        
        print("Bảng 'user' đã được tạo hoặc đã tồn tại.")

        conn.commit()
        self.close(cursor, conn)

    def get_user_by_email_and_password(self, email, password):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # Example hash
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, hashed_password))
        return cursor.fetchone()
    
    def create_user(self, first_name, last_name, email, password, mobile, user_type):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # Hash password before storing
        cursor.execute("""
            INSERT INTO `user` (first_name, last_name, email, password, mobile, type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, hashed_password, mobile, user_type))
        conn.commit()
        self.close(cursor, conn)

    def get_all_teachers(self):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('SELECT t.teacher_id, t.teacher, s.subject FROM teacher t LEFT JOIN subjects s ON s.subject_id = t.subject_id')
        return cursor.fetchall()
    
    def get_teacher_by_id(self, teacher_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('''
            SELECT t.teacher_id, t.teacher, s.subject 
            FROM teacher t 
            LEFT JOIN subjects s ON s.subject_id = t.subject_id 
            WHERE t.teacher_id = %s
        ''', (teacher_id,))
        return cursor.fetchall()
    
    def save_teacher(self, techer_name, specialization, teacherid=None):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        if teacherid:
            cursor.execute('UPDATE teacher SET teacher = %s, subject_id = %s WHERE teacher_id = %s', (techer_name, specialization, teacherid))
        else:
            cursor.execute('INSERT INTO teacher (`teacher`, `subject_id`) VALUES (%s, %s)', (techer_name, specialization))
        conn.commit()

    def delete_teacher(self, teacher_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('DELETE FROM teacher WHERE teacher_id = %s', (teacher_id,))
        conn.commit()


    def get_all_subjects(self):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('SELECT * FROM subjects')
        return cursor.fetchall()
    
    def get_subject_by_id(self, subject_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('SELECT subject_id, subject, type, code FROM subjects WHERE subject_id = %s', (subject_id,))
        return cursor.fetchall()
    
    def save_subject(self, subject, s_type, code, subject_id=None):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        if subject_id:
            cursor.execute('UPDATE subjects SET subject = %s, type = %s, code = %s WHERE subject_id = %s', 
                           (subject, s_type, code, subject_id))
        else:
            cursor.execute('INSERT INTO subjects (`subject`, `type`, `code`) VALUES (%s, %s, %s)', 
                           (subject, s_type, code))
        conn.commit()

    def delete_subject(self, subject_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('DELETE FROM subjects WHERE subject_id = %s', (subject_id,))
        conn.commit()
    

    def get_all_classes(self):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('SELECT c.id, c.name, s.section, t.teacher FROM classes c LEFT JOIN section s ON s.section_id = c.section LEFT JOIN teacher t ON t.teacher_id = c.teacher_id')
        return cursor.fetchall()
    
    def get_class_by_id(self, class_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('SELECT c.id, c.name, s.section, t.teacher FROM classes c LEFT JOIN section s ON s.section_id = c.section LEFT JOIN teacher t ON t.teacher_id = c.teacher_id WHERE c.id = %s', (class_id,))
        return cursor.fetchall()
    
    def save_class(self, cname, sectionid, teacherid, class_id=None):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
    
        if class_id:
            cursor.execute('UPDATE classes SET name = %s, section = %s, teacher_id = %s WHERE id = %s', (cname, sectionid, teacherid, class_id))
        else:
            cursor.execute('INSERT INTO classes (name, section, teacher_id) VALUES (%s, %s, %s)', (cname, sectionid, teacherid))
        conn.commit()

    def delete_class(self, class_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('DELETE FROM classes WHERE id = %s', (class_id,))
        conn.commit()

    def get_all_sections(self):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('SELECT * FROM section')
        return cursor.fetchall()
    
    def get_section_by_id(self, section_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('SELECT * FROM section WHERE section_id = %s', (section_id,))
        return cursor.fetchall()
    
    def save_section(self, section_name, section_id=None):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        if section_id:
            cursor.execute('UPDATE section SET section = %s WHERE section_id = %s', (section_name, section_id))
        else:
            cursor.execute('INSERT INTO section (`section`) VALUES (%s)', (section_name,))
        conn.commit()

    def delete_section(self, section_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('DELETE FROM section WHERE section_id = %s', (section_id,))
        conn.commit()


    def get_all_students(self):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        query = '''
            SELECT 
                s.id, s.name, s.gender, s.dob, s.mobile, s.email, 
                s.current_address, s.class, s.section, s.stream, 
                s.admission_date, s.academic_year, 
                c.name AS class_name, sec.section AS section_name
            FROM students s
            LEFT JOIN classes c ON c.id = s.class
            LEFT JOIN section sec ON sec.section_id = s.section
        '''
        cursor.execute(query)
        return cursor.fetchall()
    
    def get_student_by_id(self, student_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        query = '''
            SELECT 
                s.id, s.name, s.gender, s.dob, s.mobile, s.email, 
                s.current_address, s.class, s.section, s.stream, 
                s.admission_date, s.academic_year
            FROM students s
            WHERE s.id = %s
        '''
        cursor.execute(query, (student_id,))
        return cursor.fetchone()
    
    def save_student(self, student_data, student_id=None):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        if student_id:
            query = '''
                UPDATE students 
                SET name = %s, gender = %s, dob = %s, mobile = %s, 
                    email = %s, current_address = %s, class = %s, 
                    section = %s, stream = %s, admission_date = %s, 
                    academic_year = %s
                WHERE id = %s
            '''
            cursor.execute(query, (
                student_data['name'], student_data['gender'], 
                student_data['dob'], student_data['mobile'], 
                student_data['email'], student_data['current_address'], 
                student_data['class_id'], student_data['section_id'], 
                student_data.get('stream'), student_data['admission_date'], 
                student_data['academic_year'], student_id
            ))
        else:
            query = '''
                INSERT INTO students 
                (name, gender, dob, mobile, email, current_address, class, 
                section, stream, admission_date, academic_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(query, (
                student_data['name'], student_data['gender'], 
                student_data['dob'], student_data['mobile'], 
                student_data['email'], student_data['current_address'], 
                student_data['class_id'], student_data['section_id'], 
                student_data.get('stream'), student_data['admission_date'], 
                student_data['academic_year']
            ))
        conn.commit()

    def delete_student(self, student_id):
        conn, cursor = self.connect()
        self.useGuiDB(cursor)
        cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
        conn.commit()
    


    # def save_student(self, name, gender, dob, mobile, email, current_address, class_id, section_id, stream=None, admission_date=None, academic_year=None, student_id=None):
    #     conn, cursor = self.connect()
    #     self.useGuiDB(cursor)
    #     if student_id:
    #     # Cập nhật sinh viên nếu student_id đã tồn tại
    #         cursor.execute('''
    #             UPDATE students 
    #             SET name = %s, gender = %s, dob = %s, mobile = %s, email = %s, current_address = %s, class = %s, section = %s, stream = %s, admission_date = %s, academic_year = %s 
    #             WHERE id = %s
    #         ''', (name, gender, dob, mobile, email, current_address, class_id, section_id, stream, admission_date, academic_year, student_id))
    #     else:
    #     # Thêm mới sinh viên nếu student_id không tồn tại
    #         cursor.execute('''
    #             INSERT INTO students (name, gender, dob, mobile, email, current_address, class, section, stream, admission_date, academic_year) 
    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #         ''', (name, gender, dob, mobile, email, current_address, class_id, section_id, stream, admission_date, academic_year))
    #     conn.commit()

    # def delete_student(self, student_id):
    #     conn, cursor = self.connect()
    #     self.useGuiDB(cursor)
    #     cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
    #     conn.commit()
if __name__ == '__main__':
    db = Database()
    # db.createGuiDB()
    db.createTables()
