"""
Fee calculation service.

This module is the primary target for white-box testing (statement &
branch coverage) in the QA project, since every function here has
multiple decision branches driven by financial edge cases.
"""
from decimal import Decimal
from app.models import FeeStructure, Discount, Payment, Student, Term


def get_total_fees(student_id: int, term_id: int) -> Decimal:
    student = Student.query.get(student_id)
    if student is None:
        raise ValueError("Invalid student")
    rows = FeeStructure.query.filter_by(class_id=student.class_id, term_id=term_id).all()
    total = sum((row.amount for row in rows), Decimal("0"))
    return Decimal(total)


def get_total_discount(student_id: int, term_id: int) -> Decimal:
    rows = Discount.query.filter_by(student_id=student_id, term_id=term_id).all()
    total = sum((row.amount for row in rows), Decimal("0"))
    return Decimal(total)


def get_net_fees(student_id: int, term_id: int) -> Decimal:
    total_fees = get_total_fees(student_id, term_id)
    total_discount = get_total_discount(student_id, term_id)
    net = total_fees - total_discount
    # Business rule: net fees can never be negative, even if discounts
    # exceed the fee total (edge case explicitly covered in test suite).
    if net < 0:
        net = Decimal("0")
    return net


def get_total_payments(student_id: int, term_id: int) -> Decimal:
    rows = Payment.query.filter_by(student_id=student_id, term_id=term_id, status="confirmed").all()
    total = sum((row.amount for row in rows), Decimal("0"))
    return Decimal(total)


def get_balance(student_id: int, term_id: int) -> Decimal:
    """Balance = Net Fees - Total Confirmed Payments."""
    net_fees = get_net_fees(student_id, term_id)
    total_payments = get_total_payments(student_id, term_id)
    return net_fees - total_payments


def get_student_fee_summary(student_id: int, term_id: int) -> dict:
    student = Student.query.get(student_id)
    if student is None:
        raise ValueError("Invalid student")
    term = Term.query.get(term_id)
    if term is None:
        raise ValueError("Invalid term")

    total_fees = get_total_fees(student_id, term_id)
    total_discount = get_total_discount(student_id, term_id)
    net_fees = get_net_fees(student_id, term_id)
    total_payments = get_total_payments(student_id, term_id)
    balance = net_fees - total_payments

    return {
        "student_id": student_id,
        "term_id": term_id,
        "total_fees": float(total_fees),
        "total_discount": float(total_discount),
        "net_fees": float(net_fees),
        "total_payments": float(total_payments),
        "balance": float(balance),
        "status": "fully_paid" if balance <= 0 else "outstanding",
    }
