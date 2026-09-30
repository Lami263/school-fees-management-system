import pytest
from datetime import date
from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import User, ClassRoom, Term, Student, FeeStructure


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app


@pytest.fixture()
def db_session(app):
    yield db.session
    db.session.rollback()


@pytest.fixture()
def admin_user(app):
    user = User(username="admin_test", role="admin")
    user.set_password("pass1234")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def bursar_user(app):
    user = User(username="bursar_test", role="bursar")
    user.set_password("pass1234")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def sample_class(app):
    c = ClassRoom(name="Form 1A", level="Secondary")
    db.session.add(c)
    db.session.commit()
    return c


@pytest.fixture()
def sample_term(app):
    t = Term(name="Term 1", academic_year="2026",
              start_date=date(2026, 1, 12), end_date=date(2026, 4, 3))
    db.session.add(t)
    db.session.commit()
    return t


@pytest.fixture()
def sample_student(app, sample_class):
    s = Student(admission_no="ADM001", first_name="Tendai", last_name="Moyo",
                class_id=sample_class.id, status="active")
    db.session.add(s)
    db.session.commit()
    return s


@pytest.fixture()
def fee_structure(app, sample_class, sample_term):
    """Total fees for the student = 300 (Tuition 250 + Levy 50)."""
    f1 = FeeStructure(class_id=sample_class.id, term_id=sample_term.id, fee_type="Tuition", amount=250)
    f2 = FeeStructure(class_id=sample_class.id, term_id=sample_term.id, fee_type="Levy", amount=50)
    db.session.add_all([f1, f2])
    db.session.commit()
    return [f1, f2]
