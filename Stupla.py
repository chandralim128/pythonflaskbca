#Import Library

from flask import Flask, jsonify, request, render_template
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import joinedload, relationship
from datetime import datetime
from flasgger import Swagger, swag_from
import os

#Mendefinisikan app
app = Flask(__name__)

# Lokasi Database
DATABASE_PATH = 'C:\\MyFile\\TrainingFlask\\project\\StudyPlatform\\Stupla.db'

# Konfigurasi Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:ifapi3HmRFiGKYnwtYe0@containers-us-west-157.railway.app:5474/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Konfigurasi Swagger
app.config['SWAGGER'] = {
    'title': 'Data StudyPlatform',
    'uiversion': 3,
    'headers': [],
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/apispec_1.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_router': '/apidocs/'
}

swagger = Swagger(app)

db = SQLAlchemy(app)

# Model Data Courses
class Courses(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(255), nullable=False)
    instructor = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    enrollment = relationship('Enrollments', back_populates='course',cascade='all, delete-orphan')

# Model Data Enrollments
class Enrollments(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, ForeignKey('courses.course_id'))
    enrollment_date = db.Column(db.Date, nullable=False)
    completion_date = db.Column(db.Date, nullable=False)
    course = relationship('Courses', back_populates='enrollment')

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

#Koneksi API create course
@app.route('/course', methods=['POST'])
@swag_from('swagger_docs/create_data_courses.yaml')
def create_course():
    # Mendapatkan data dari permintaan POST
    data = request.json

    # Membuat objek Courses
    new_course = Courses(
        title=data['title'],
        instructor=data['instructor'],
        category=data['category'],
        price = data['price']
    )
    #Menyimpan objek ke database
    db.session.add(new_course)
    db.session.commit()

    # Mengembalikan respons HTTP 201 Created
    return jsonify({'message': 'Data course berhasil ditambahkan'}), 201

#Koneksi API create enrollment
@app.route('/enrollments', methods=['POST'])
@swag_from('swagger_docs/create_data_enrollments.yaml')
def create_enrollments():
    # Mendapatkan data dari permintaan POST
    data = request.json

    # Membuat objek Enrollments
    new_enrollment = Enrollments(
        user_id=data['user_id'],
        course_id=data['course_id'],
        enrollment_date=data['enrollment_date'],
        completion_date = data['completion_date']
    )
    #Menyimpan objek ke database
    db.session.add(new_enrollment)
    db.session.commit()

    # Mengembalikan respons HTTP 201 Created
    return jsonify({'message': 'Data enrollment berhasil ditambahkan'}), 201


#Fungsi Menambahkan Data Course
@app.route('/inputCourse', methods=['GET', 'POST'])
def input_data_course():
    if request.method == 'POST':
        #Mendapatkan data dari form
        title = request.form.get('title')
        instructor = request.form.get('instructor')
        category = request.form.get('category')
        price = request.form.get('price')

        #Membuat objek karyawan
        new_course = Courses(
            title=title,
            instructor=instructor,
            category=category,
            price = price
        )
        #Proses simpan data
        db.session.add(new_course)
        db.session.commit()

        #Mengarahkan ke halaman konfirmasi 
        return render_template('confirmationCourse.html')
    return render_template('createdatacourse.html')

#Fungsi Menambahkan Data Enrollment
@app.route('/inputEnrollment', methods=['GET', 'POST'])
def input_data_enrollment():
    if request.method == 'POST':
        try:
            #Mendapatkan data dari form
            user_id = request.form.get('user_id')
            course_title= request.form.get('course_title')
            enrollment_date = datetime.strptime(request.form.get('enrollment_date'), '%Y-%m-%d').date()
            completion_date = datetime.strptime(request.form.get('completion_date'), '%Y-%m-%d').date()
            # Validasi tanggal
            if enrollment_date > completion_date:
                return render_template('error.html', pesan="enrollment date melebihi completion date"), 400

            data_course = Courses.query.filter(Courses.title.like(f"%{course_title}%")).first()
            #Mengecek data course
            if not data_course:
                return render_template('error.html', pesan="Data Course tidak ditemukan"), 404
            #Membuat objek enrollments
            new_enrollment = Enrollments(
                user_id=user_id,
                course_id = data_course.course_id,
                enrollment_date=enrollment_date,
                completion_date=completion_date
            )
            #Proses simpan data
            db.session.add(new_enrollment)
            db.session.commit()

            #Mengarahkan ke halaman konfirmasi 
            return render_template('confirmationEnrollment.html')
        except Exception as e:
            return jsonify({'message':f'Terjadi kesalahan: {str(e)}'}), 500
    
    return render_template('createdataenrollment.html')

@app.route('/display_all_courses', methods=['GET'])
@swag_from('swagger_docs/get_all_data_courses.yaml')
def get_all_courses():
    courses_list = []
    try:
        #Mengambil semua data courses dari database
        all_courses = Courses.query.all()
        # Membuat daftar dari data courses untuk dikirimkan ke template
        for course in all_courses:
            course_data={
                'course_id': course.course_id,
                'instructor': course.instructor,
                'title': course.title,
                'category': course.category,
                'price': course.price
            }
            courses_list.append(course_data)
    except Exception as e:
        #Mengembalikan pesan kesalahan dalam Bahasa Indonesia jika terjadi kesalahan
        return render_template('error.html', pesan='Terjadi kesalahan saat mengambil data')
    finally:
        #Mengembalikan template dengan data courses jika tidak ada kesalahan
        if courses_list:
            return render_template('displayallcourses.html', courses_list=courses_list)
        else:
            #Mengembalikan pesan kesalahan jika tidak ada data courses
            return render_template('error.html', pesan="Tidak ada data"
                                   "course yang dapat ditampilkan."), 404
        
@app.route('/display_all_enrollments', methods=['GET'])
@swag_from('swagger_docs/get_all_data_enrollments.yaml')
def get_all_enrollments():
    enrollments_list = []
    try:
        #Mengambil semua data enrollment dari database
        query = db.session.query(Enrollments)
        all_enrollments = query.all()
        # Membuat daftar dari data Enrollments untuk dikirimkan ke template
        for enrollment in all_enrollments:
            enrollment_data={
                'enrollment_id': enrollment.enrollment_id,
                'user_id': enrollment.user_id,
                'course_title': enrollment.course.title,
                'enrollment_date': enrollment.enrollment_date,
                'completion_date': enrollment.completion_date
            }
            enrollments_list.append(enrollment_data)
    except Exception as e:
        #Mengembalikan pesan kesalahan dalam Bahasa Indonesia jika terjadi kesalahan
        return render_template('error.html', pesan='Terjadi kesalahan saat mengambil data')
    finally:
        #Mengembalikan template dengan data enrollments jika tidak ada kesalahan
        if enrollments_list:
            return render_template('displayallenrollments.html', enrollments_list=enrollments_list)
        else:
            #Mengembalikan pesan kesalahan jika tidak ada data enrollment
            return render_template('error.html', pesan="Tidak ada data"
                                   "enrollment yang dapat ditampilkan."), 404
        
@app.route('/update_data_course', methods=['GET', 'POST'])
def updatedatacourse():
    if request.method == 'POST':
        title = request.form.get('title')
        data_list = Courses.query.filter(Courses.title.like(f"%{title}%")).all()
        return render_template('updatedatacourse.html', data_list=data_list)
    return render_template('updatedatacourse.html')

@app.route('/update_course', methods=['POST'])
def update_course():
    try:
        course_id = request.form.get('course_id')
        title = request.form.get('title')
        instructor = request.form.get('instructor')
        category = request.form.get('category')
        price = request.form.get('price')

        course = Courses.query.get(course_id)

        if not course:
                return jsonify({'message':'Course tidak ditemukan'}, 404)
        
        course.course_id = course_id
        course.title = title
        course.instructor = instructor
        course.category = category
        course.price = price

        db.session.commit()

        return redirect(url_for('get_all_courses'))
    except Exception as e:
        return jsonify({'message':f'Terjadi kesalahan: {str(e)}'}), 500

@app.route('/update_data_enrollment', methods=['GET', 'POST'])
def updatedataenrollment():
    if request.method == 'POST':
        user_id = request.form.get('user')
        data_list = Enrollments.query.filter(Enrollments.user_id.like(f"%{user_id}%")).all()
        return render_template('updatedataenrollment.html', data_list=data_list)
    return render_template('updatedataenrollment.html')

@app.route('/update_enrollment', methods=['POST'])
def update_enrollment():
    try:
        enrollment_id = request.form.get('enrollment_id')
        user_id = request.form.get('user_id')
        enrollment_date = datetime.strptime(request.form.get('enrollment_date'), '%Y-%m-%d').date()
        completion_date = datetime.strptime(request.form.get('completion_date'), '%Y-%m-%d').date()

        enrollment = Enrollments.query.get(enrollment_id)

        if not enrollment:
                return jsonify({'message':'Enrollment tidak ditemukan'}, 404)
        
        enrollment.enrollment_id = enrollment_id
        enrollment.user_id = user_id
        enrollment.enrollment_date = enrollment_date
        enrollment.completion_date = completion_date
        db.session.commit()

        return redirect(url_for('get_all_enrollments'))
    except Exception as e:
        return jsonify({'message':f'Terjadi kesalahan: {str(e)}'}), 500
    
@app.route('/delete_course', methods=['GET', 'POST'])
def delete_course_ui():
    data_list = []
    try:
        if request.method == 'POST':
            search_title = request.form['title'].lower()
            all_course = Courses.query.all()
            data_list = [course for course in all_course if search_title in course.title.lower()]
    except Exception as e:
        error_message = f"Terjadi kesalahan: {e}"
        print(error_message)
        return render_template('error.html', pesan = error_message), 500
    finally:
        return render_template('deletedatacourse.html', data_list=data_list)
    
@app.route('/course/<int:course_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_data_courses.yaml')
def delete_course(course_id):
    try:
        course_to_delete = Courses.query.filter_by(course_id=course_id).first()
        if course_to_delete:
            db.session.delete(course_to_delete)
            db.session.commit()
            return jsonify({'message': f'Data course dengan ID {course_id} berhasil dihapus'}), 200
        else:
            return jsonify({'message': f'Data course dengan ID {course_id} tidak ditemukan'}), 404
    except Exception as e:
        return jsonify ({'message': f'Terjadi kesalahan: {e}'}), 500

@app.route('/delete_enrollment', methods=['GET', 'POST'])
def delete_enrollment_ui():
    data_list = []
    try:
        if request.method == 'POST':
            search_user = request.form['user_id'].lower()
            all_enrollment = Enrollments.query.all()
            data_list = [enrollment for enrollment in all_enrollment if search_user in enrollment.user_id.lower()]
    except Exception as e:
        error_message = f"Terjadi kesalahan: {e}"
        return render_template('error.html', pesan = error_message), 500
    finally:
        return render_template('deletedataenrollment.html', data_list=data_list)
    
@app.route('/enrollment/<int:enrollment_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_data_enrollments.yaml')
def delete_enrollment(enrollment_id):
    try:
        enrollment_to_delete = Enrollments.query.filter_by(enrollment_id=enrollment_id).first()
        if enrollment_to_delete:
            db.session.delete(enrollment_to_delete)
            db.session.commit()
            return jsonify({'message': f'Data course dengan ID {enrollment_id} berhasil dihapus'}), 200
        else:
            return jsonify({'message': f'Data course dengan ID {enrollment_id} tidak ditemukan'}), 404
    except Exception as e:
        return jsonify ({'message': f'Terjadi kesalahan: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5030)
