import unittest
from flask_testing import TestCase
from flask import url_for
from Stupla import app, db, Courses, Enrollments  # Import modul-modul yang diperlukan
from datetime import datetime
# Kelas MyTest untuk melakukan testing pada aplikasi
class MyTest(TestCase):

    # Metode untuk membuat aplikasi dalam mode testing
    def create_app(self):
        DATABASE_PATH = 'C:\\MyFile\\TrainingFlask\\project\\StudyPlatform\\Stupla.db'
        app.config['TESTING'] = True  # Mengaktifkan mode testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH  # Menggunakan database in-memory untuk testing
        return app

    # Metode yang dijalankan sebelum setiap test
    def setUp(self):
        db.create_all()  # Membuat semua tabel dalam database

    # Metode yang dijalankan setelah setiap test
    # def tearDown(self):
    #     db.session.remove()  # Menghapus sesi database
    #     db.drop_all()  # Menghapus semua tabel dalam database

    # Test untuk endpoint index '/'
    def test_index(self):
        response = self.client.get('/')  # Melakukan request GET ke '/'
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('index.html')  # Memastikan template yang digunakan adalah 'index.html'

    # Test untuk membuat karyawan baru
    def test_create_course(self):
        # Melakukan request POST ke '/karyawan' dengan data karyawan baru
        response = self.client.post('/course', json={
            'title': 'React',
            'instructor': 'Filbert',
            'category': 'Coding',
            'price': 1000 
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        course = Courses.query.first()  # Mengambil course pertama dari database
        self.assertEqual(course.title, 'React')  # Memastikan nama course adalah 'React'

    # Test untuk menghapus course
    def test_delete_course(self):
        # Membuat objek course baru dan menyimpannya ke database
        course = Courses(title='Swift', instructor='Isa', category='Coding', price=10000)
        db.session.add(course)
        db.session.commit()

        # Melakukan request DELETE ke '/course/{course_id}'
        response = self.client.delete(f'/course/{course.course_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(Courses.query.get(course.course_id))  # Memastikan karyawan dengan id tersebut sudah dihapus

    # Test untuk mendapatkan semua karyawan
    def test_get_all_courses(self):
        # Membuat dua objek karyawan baru dan menyimpannya ke database
        course1 = Courses(title='Ninjutsu', instructor='Alek', category='Coding', price=100000)
        course2 = Courses(title='Genjutsu', instructor='Alek', category='Coding', price=200000)
        db.session.add(course1)
        db.session.add(course2)
        db.session.commit()

        # Melakukan request GET ke '/display_all'
        response = self.client.get('/display_all_courses')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('displayallcourses.html')  # Memastikan template yang digunakan adalah 'displayall.html'
        self.assertIn(b'Ninjutsu', response.data)  # Memastikan 'John Doe' ada dalam response data
        self.assertIn(b'Genjutsu', response.data)  # Memastikan 'Jane Doe' ada dalam response data
    
    # Test untuk membuat enrollment baru
    def test_create_enrollment(self):
        # Melakukan request POST ke '/karyawan' dengan data karyawan baru
        response = self.client.post('/enrollments', json={
            'user_id': 'Lim',
            'course_id': '1',
            'enrollment_date': '2023-09-25',
            'completion_date': '2023-10-25'
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        enrollment = Enrollments.query.first()  # Mengambil course pertama dari database
        self.assertEqual(enrollment.user_id, 'Lim')  # Memastikan nama course adalah 'React'

    # # Test untuk menghapus karyawan
    def test_delete_enrollment(self):
        # Membuat objek karyawan baru dan menyimpannya ke database
        enrollment_date = datetime.strptime('2023-09-25', '%Y-%m-%d').date()
        completion_date = datetime.strptime('2023-10-25', '%Y-%m-%d').date()
        enrollment = Enrollments(user_id='Hal', course_id='1', enrollment_date=enrollment_date,completion_date=completion_date)
        db.session.add(enrollment)
        db.session.commit()

        # Melakukan request DELETE ke '/course/{course_id}'
        response = self.client.delete(f'/enrollment/{enrollment.enrollment_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(Enrollments.query.get(enrollment.enrollment_id))  # Memastikan karyawan dengan id tersebut sudah dihapus

    # Test untuk mendapatkan semua karyawan
    def test_get_all_enrollments(self):
        # Membuat dua objek karyawan baru dan menyimpannya ke database
        edate1 = datetime.strptime('2023-09-25', '%Y-%m-%d').date()
        cdate1 = datetime.strptime('2023-10-25', '%Y-%m-%d').date()
        edate2 = datetime.strptime('2023-11-25', '%Y-%m-%d').date()
        cdate2 = datetime.strptime('2023-12-25', '%Y-%m-%d').date()
        
        enrollment1 = Enrollments(user_id='Hal', course_id=1, enrollment_date= edate1,completion_date= cdate1)
        db.session.add(enrollment1)
        db.session.commit()
        enrollment2 = Enrollments(user_id='Chan', course_id=1, enrollment_date= edate2,completion_date= cdate2)
        db.session.add(enrollment2)
        db.session.commit()
        # Melakukan request GET ke '/display_all'
        response = self.client.get('/display_all_enrollments')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('displayallenrollments.html')  # Memastikan template yang digunakan adalah 'displayall.html'
        self.assertIn(b'Hal', response.data)  # Memastikan 'John Doe' ada dalam response data
        self.assertIn(b'Chan', response.data)  # Memastikan 'Jane Doe' ada dalam response data


if __name__ == '__main__':
    unittest.main()  # Menjalankan semua test