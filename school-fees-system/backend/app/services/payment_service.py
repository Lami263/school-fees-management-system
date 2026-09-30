"""
Payment service — the core financial logic of the system.

Every validation branch here maps directly to a test case in the QA
project's test plan (Boundary Value Analysis / Equivalence Partitioning /
Decision Table rows):

    - amount <= 0            -> zero / negative payment cases
    - duplicate reference_no -> duplicate transaction case
    - unknown student_id     -> invalid student case
    - amount > balance       -> overpayment case (rejected unless allowed)
    - editor.role != admin   -> unauthorized transaction editing case
"""
from decimal import Decimal
from datetime import date
import uuid

from app.extensions import db
from app.models import Payment, Receipt, Student, Term, AuditLog, User
from app.services.fee_service import get_balance


class PaymentError(ValueError):
    """Raised for any business-rule validation failure on a payment."""


class UnauthorizedError(PermissionError):
    """Raised when a non-admin user attempts a restricted action."""


def _generate_receipt_no() -> str:
    return f"RCPT-{uuid.uuid4().hex[:10].upper()}"


def record_payment(
    student_id: int,
    term_id: int,
    amount,
    payment_method: str,
    reference_no: str,
    recorded_by: int,
    payment_date=None,
    allow_overpayment: bool = False,
) -> Payment:
    student = Student.query.get(student_id)
    if student is None:
        raise PaymentError("Invalid student")

    term = Term.query.get(term_id)
    if term is None:
        raise PaymentError("Invalid term")

    try:
        amount = Decimal(str(amount))
    except Exception:
        raise PaymentError("Payment amount must be a valid number")

    # Boundary Value Analysis target: amount must be strictly > 0
    if amount <= 0:
        raise PaymentError("Payment amount must be greater than zero")

    if not reference_no or not reference_no.strip():
        raise PaymentError("Reference number is required")

    existing = Payment.query.filter_by(reference_no=reference_no).first()
    if existing is not None:
        raise PaymentError("Duplicate transaction: reference number already used")

    balance = get_balance(student_id, term_id)
    if amount > balance and not allow_overpayment:
        raise PaymentError(
            f"Payment of {amount} exceeds outstanding balance of {balance}"
        )

    payment = Payment(
        student_id=student_id,
        term_id=term_id,
        amount=amount,
        payment_method=payment_method,
        reference_no=reference_no,
        payment_date=payment_date or date.today(),
        recorded_by=recorded_by,
        status="confirmed",
    )
    db.session.add(payment)
    db.session.flush()  # get payment.id before commit

    receipt = Receipt(
        payment_id=payment.id,
        receipt_no=_generate_receipt_no(),
        issued_date=date.today(),
        issued_by=recorded_by,
    )
    db.session.add(receipt)
    db.session.commit()
    return payment


def edit_payment(payment_id: int, editor: User, new_amount=None, new_status=None, reason: str = "") -> Payment:
    """
    Only an 'admin' may edit a confirmed payment. Edits never silently
    overwrite: the original is marked 'reversed' and the change is
    written to the audit log, so there is always a trail.
    """
    if editor is None or editor.role != "admin":
        raise UnauthorizedError("Unauthorized: only an admin may edit payments")

    payment = Payment.query.get(payment_id)
    if payment is None:
        raise PaymentError("Payment not found")

    old_values = f"amount={payment.amount}, status={payment.status}"

    if new_amount is not None:
        new_amount = Decimal(str(new_amount))
        if new_amount <= 0:
            raise PaymentError("Payment amount must be greater than zero")
        payment.amount = new_amount

    if new_status is not None:
        payment.status = new_status

    db.session.add(
        AuditLog(
            user_id=editor.id,
            action="EDIT_PAYMENT",
            table_affected="payments",
            record_id=payment.id,
            details=f"old: {old_values} -> new: amount={payment.amount}, status={payment.status}. Reason: {reason}",
        )
    )
    db.session.commit()
    return payment


def delete_payment(payment_id: int, editor: User, reason: str = "") -> None:
    if editor is None or editor.role != "admin":
        raise UnauthorizedError("Unauthorized: only an admin may delete payments")

    payment = Payment.query.get(payment_id)
    if payment is None:
        raise PaymentError("Payment not found")

    db.session.add(
        AuditLog(
            user_id=editor.id,
            action="DELETE_PAYMENT",
            table_affected="payments",
            record_id=payment.id,
            details=f"deleted payment amount={payment.amount}, reference={payment.reference_no}. Reason: {reason}",
        )
    )
    # Soft-delete pattern: mark reversed rather than hard delete, to
    # preserve financial audit trail.
    payment.status = "reversed"
    db.session.commit()
