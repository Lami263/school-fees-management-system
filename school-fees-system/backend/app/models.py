from datetime import datetime, date
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="bursar")  # admin, bursar, parent
    email = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "role": self.role, "email": self.email}


class ClassRoom(db.Model):
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    level = db.Column(db.String(20))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "level": self.level}


class Term(db.Model):
    __tablename__ = "terms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    academic_year = db.Column(db.String(9), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "academic_year": self.academic_year,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"))
    guardian_name = db.Column(db.String(100))
    guardian_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="active")  # active, graduated, withdrawn
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class_room = db.relationship("ClassRoom", backref="students")

    def to_dict(self):
        return {
            "id": self.id,
            "admission_no": self.admission_no,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "dob": self.dob.isoformat() if self.dob else None,
            "gender": self.gender,
            "class_id": self.class_id,
            "class_name": self.class_room.name if self.class_room else None,
            "guardian_name": self.guardian_name,
            "guardian_phone": self.guardian_phone,
            "status": self.status,
        }


class FeeStructure(db.Model):
    __tablename__ = "fee_structures"
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=False)
    fee_type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (db.CheckConstraint("amount >= 0", name="ck_fee_amount_nonneg"),)

    def to_dict(self):
        return {
            "id": self.id,
            "class_id": self.class_id,
            "term_id": self.term_id,
            "fee_type": self.fee_type,
            "amount": float(self.amount),
        }


class Discount(db.Model):
    __tablename__ = "discounts"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)  # scholarship, sibling, staff, other
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.CheckConstraint("amount >= 0", name="ck_discount_amount_nonneg"),)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "term_id": self.term_id,
            "discount_type": self.discount_type,
            "amount": float(self.amount),
            "reason": self.reason,
            "approved_by": self.approved_by,
        }


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, bank_transfer, mobile_money, cheque
    reference_no = db.Column(db.String(50), unique=True, nullable=False)
    payment_date = db.Column(db.Date, default=date.today)
    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(20), default="confirmed")  # confirmed, reversed, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.CheckConstraint("amount > 0", name="ck_payment_amount_positive"),)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "term_id": self.term_id,
            "amount": float(self.amount),
            "payment_method": self.payment_method,
            "reference_no": self.reference_no,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "recorded_by": self.recorded_by,
            "status": self.status,
        }


class Receipt(db.Model):
    __tablename__ = "receipts"
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), unique=True, nullable=False)
    receipt_no = db.Column(db.String(30), unique=True, nullable=False)
    issued_date = db.Column(db.Date, default=date.today)
    issued_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    payment = db.relationship("Payment", backref="receipt")

    def to_dict(self):
        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "receipt_no": self.receipt_no,
            "issued_date": self.issued_date.isoformat() if self.issued_date else None,
            "issued_by": self.issued_by,
        }


class AuditLog(db.Model):
    __tablename__ = "audit_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(50), nullable=False)
    table_affected = db.Column(db.String(50))
    record_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "table_affected": self.table_affected,
            "record_id": self.record_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "details": self.details,
        }
