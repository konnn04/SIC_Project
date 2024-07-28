import sys
import os

# Thêm đường dẫn tới thư mục chứa module 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import date, time
from app import db, Class, Student, Label, StudentCheckIn, app
import random


def populate_db():
    # Tạo dữ liệu mẫu cho bảng Class
    class1 = Class(class_id='IT01', class_name='CNTT 1')
    class2 = Class(class_id='IT02', class_name='CNTT 2')
    class3 = Class(class_id='CS01', class_name='CS 1')
    class4 = Class(class_id='CS02', class_name='CS 2')

    # Tạo dữ liệu mẫu cho bảng Student
    # Function to generate random sex
    def generate_sex():
        sexes = ['Nam', 'Nữ']
        return random.choice(sexes)

    # Function to generate random class
    def generate_class():
        classes = ['IT01', 'IT02', 'CS01', 'CS02']
        return random.choice(classes)

    # Function to generate random birthdate
    def generate_birthdate():
        year = random.randint(1990, 2005)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return date(year, month, day)

    # Function to generate random address
    def generate_address():
        streets = ['Main St', 'Elm St', 'Oak St', 'Maple Ave']
        numbers = ['123', '456', '789', '1011']
        street = random.choice(streets)
        number = random.choice(numbers)
        return f"{number} {street}"

    # Get list of subdirectories in /dataset/processed
    subdirectories = [x[0] for x in os.walk('dataset/processed')][1:]

    students = []
    student_id = 1
    print(subdirectories)

    # Loop through each subdirectory
    for directory in subdirectories:
        svfname = os.path.basename(directory)
        sex = generate_sex()
        class_id = generate_class()
        birthdate = generate_birthdate()
        address = generate_address()

        student = Student(
            student_id=student_id,
            svfname=svfname,
            svlname=['Nguyen', 'Tran', 'Le', 'Pham'][random.randint(0, 3)],
            sex=sex,
            birthdate=birthdate,
            address=address,
            class_id=class_id
        )

        students.append(student)
        student_id += 1

    # Add students to the database
    db.session.add_all(students)
    db.session.commit()

    # Tạo dữ liệu mẫu cho bảng Label
    # Tạo dữ liệu mẫu cho bảng Label
    labels = []
    for student in students:
        label = Label(student_id=student.student_id, label_name=student.svfname)
        labels.append(label)

    # Add labels to the database
    db.session.add_all(labels)


    # Thêm dữ liệu vào session và commit
    db.session.add_all([class1, class2, class3, class4] if not db.session.query(Class).all() else [])
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        populate_db()
        print("Database populated with sample data.")