# seed_users.py

from app import app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

mock_students = [
    # Computer Science Students
    {
        "roll_number": "BSCS022R24-10",
        "name": "Ahmed Ali Khan",
        "password": "usp2021cs001",
        "department": "Computer Science",
        "semester": 8
    },
    {
        "roll_number": "BSCS022R24-17", 
        "name": "Sara Fatima",
        "password": "usp2021cs002",
        "department": "Computer Science",
        "semester": 8
    },
    {
        "roll_number": "BSCS022R24-41",
        "name": "Muhammad Usman",
        "password": "usp2021cs003",
        "department": "Computer Science",
        "semester": 8
    },

    # IT Students
    {
        "roll_number": "BSIT022R24-31",
        "name": "Areeba Sheikh",
        "password": "usp2021it001",
        "department": "Information Technology",
        "semester": 8
    },
    {
        "roll_number": "BSCS022R24-15",
        "name": "Ali Hassan",
        "password": "usp2021it002",
        "department": "Information Technology",
        "semester": 8
    },
    {
        "roll_number": "BSCS022R24-21",
        "name": "Zainab Malik",
        "password": "usp2021it003",
        "department": "Information Technology",
        "semester": 8
    },

    # Semester 6 Students
    {
        "roll_number": "2022-CS-001",
        "name": "Hassan Tariq",
        "password": "usp2022cs001",
        "department": "Computer Science",
        "semester": 6
    },
    {
        "roll_number": "2022-IT-001",
        "name": "Noor Fatima",
        "password": "usp2022it001",
        "department": "Information Technology",
        "semester": 6
    },

    # Semester 4 Students
    {
        "roll_number": "2023-CS-001",
        "name": "Bilal Ahmed",
        "password": "usp2023cs001",
        "department": "Computer Science",
        "semester": 4
    },
    {
        "roll_number": "2023-IT-001",
        "name": "Hira Khan",
        "password": "usp2023it001",
        "department": "Information Technology",
        "semester": 4
    },
]

with app.app_context():
    for student in mock_students:
        existing = User.query.filter_by(
            roll_number=student["roll_number"]
        ).first()
        
        if not existing:
            new_user = User(
                roll_number=student["roll_number"],
                name=student["name"],
                password=generate_password_hash(
                    student["password"]
                ),
                department=student["department"],
                semester=student["semester"]
            )
            db.session.add(new_user)
    
    db.session.commit()
    print("USP dummy users added!")
    
    users = User.query.all()
    print(f"\nTotal users: {len(users)}")
    print("\nRoll No          | Name                | Dept | Sem")
    print("-" * 60)
    for u in users:
        print(f"{u.roll_number:17}| {u.name:20}| {u.department[:2]:4} | {u.semester}")