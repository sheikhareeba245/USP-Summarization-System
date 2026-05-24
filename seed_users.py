# seed_users.py

from app import app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

mock_students = [
    # Computer Science Students
    {
        "username": "BSCS022R24-10",
        "name": "Ahmed Ali Khan",
        "password": "usp2021cs001",
        "department": "Computer Science",
        "semester": 8
    },
    {
        "username": "BSCS022R24-17", 
        "name": "Sara Fatima",
        "password": "usp2021cs002",
        "department": "Computer Science",
        "semester": 8
    },
    {
        "username": "BSCS022R24-41",
        "name": "Muhammad Usman",
        "password": "usp2021cs003",
        "department": "Computer Science",
        "semester": 8
    },

    # IT Students
    {
        "username": "BSIT022R24-31",
        "name": "Areeba Sheikh",
        "password": "usp2021it001",
        "department": "Information Technology",
        "semester": 8
    },
    {
        "username": "BSIT022R24-15",
        "name": "Ali Hassan",
        "password": "usp2021it002",
        "department": "Information Technology",
        "semester": 8
    },
    {
        "username": "BSIT022R24-21",
        "name": "Zainab Malik",
        "password": "usp2021it003",
        "department": "Information Technology",
        "semester": 8
    },

    # Semester 6 Students
    {
        "username": "2022-CS-001",
        "name": "Hassan Tariq",
        "password": "usp2022cs001",
        "department": "Computer Science",
        "semester": 6
    },
    {
        "username": "2022-IT-001",
        "name": "Noor Fatima",
        "password": "usp2022it001",
        "department": "Information Technology",
        "semester": 6
    },

    # Semester 4 Students
    {
        "username": "2023-CS-001",
        "name": "Bilal Ahmed",
        "password": "usp2023cs001",
        "department": "Computer Science",
        "semester": 4
    },
    {
        "username": "2023-IT-001",
        "name": "Hira Khan",
        "password": "usp2023it001",
        "department": "Information Technology",
        "semester": 4
    },
]

with app.app_context():
    for student in mock_students:
        existing = User.query.filter_by(
            username=student["username"]
        ).first()
        
        if not existing:
            new_user = User(
                username=student["username"],
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
    print("\nUserName          | Name                | Dept | Sem")
    print("-" * 60)
    for u in users:
        print(f"{u.username:17}| {u.name:20}| {u.department[:2]:4} | {u.semester}")