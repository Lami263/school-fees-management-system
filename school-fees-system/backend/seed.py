"""
Seed script — creates demo users, classes, terms, fee structures and
students so the frontend/API has data to exercise immediately.

Run with:  python seed.py
"""
from datetime import date
from app import create_app
from app.extensions import db
from app.models import User, ClassRoom, Term, Student, FeeStructure

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(username="admin", role="admin", email="admin@school.local")
    admin.set_password("Admin@123")
    bursar = User(username="bursar", role="bursar", email="bursar@school.local")
    bursar.set_password("Bursar@123")
    db.session.add_all([admin, bursar])

    form1 = ClassRoom(name="Form 1A", level="Secondary")
    form2 = ClassRoom(name="Form 2A", level="Secondary")
    db.session.add_all([form1, form2])

    term1 = Term(name="Term 1", academic_year="2026", start_date=date(2026, 1, 12), end_date=date(2026, 4, 3))
    db.session.add(term1)
    db.session.commit()

    fees = [
        FeeStructure(class_id=form1.id, term_id=term1.id, fee_type="Tuition", amount=500),
        FeeStructure(class_id=form1.id, term_id=term1.id, fee_type="Levy", amount=50),
        FeeStructure(class_id=form2.id, term_id=term1.id, fee_type="Tuition", amount=550),
        FeeStructure(class_id=form2.id, term_id=term1.id, fee_type="Levy", amount=50),
    ]
    db.session.add_all(fees)

    students = [
        Student(admission_no="ADM001", first_name="Tendai", last_name="Moyo",
                dob=date(2010, 3, 14), gender="M", class_id=form1.id,
                guardian_name="Mr. Moyo", guardian_phone="+263771111111"),
        Student(admission_no="ADM002", first_name="Rutendo", last_name="Chikafu",
                dob=date(2010, 7, 2), gender="F", class_id=form1.id,
                guardian_name="Mrs. Chikafu", guardian_phone="+263772222222"),
        Student(admission_no="ADM003", first_name="Tapiwa", last_name="Ncube",
                dob=date(2009, 11, 22), gender="M", class_id=form2.id,
                guardian_name="Mr. Ncube", guardian_phone="+263773333333"),
    ]
    db.session.add_all(students)
    db.session.commit()

    print("Seed complete.")
    print("Admin login  -> username: admin  password: Admin@123")
    print("Bursar login -> username: bursar password: Bursar@123")
