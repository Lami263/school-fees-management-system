"""
Unit tests for app/services/payment_service.py

This file is the direct executable implementation of the test cases
listed in the project's Test Plan:

    TC01 Full payment
    TC02 Partial payment
    TC03 Zero payment
    TC04 Overpayment
    TC05 Negative payment
    TC06 Duplicate transaction
    TC07 Invalid student
    TC08 Unauthorized transaction editing

Technique coverage: Boundary Value Analysis, Equivalence Partitioning,
Decision Table testing (role x action matrix for edit/delete).
"""
import pytest
from app.services import payment_service as ps


def _pay(**overrides):
    defaults = dict(
        payment_method="cash",
        reference_no="REF-0001",
    )
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------
# TC01 - Full payment (amount == balance)
# ---------------------------------------------------------------------
def test_full_payment_settles_balance_exactly(app, sample_student, sample_term, fee_structure, bursar_user):
    from app.services.fee_service import get_balance
    payment = ps.record_payment(
        student_id=sample_student.id, term_id=sample_term.id, amount=300,
        payment_method="cash", reference_no="REF-FULL", recorded_by=bursar_user.id,
    )
    assert payment.amount == 300
    assert get_balance(sample_student.id, sample_term.id) == 0


# ---------------------------------------------------------------------
# TC02 - Partial payment (0 < amount < balance)
# ---------------------------------------------------------------------
def test_partial_payment_reduces_balance(app, sample_student, sample_term, fee_structure, bursar_user):
    from app.services.fee_service import get_balance
    ps.record_payment(
        student_id=sample_student.id, term_id=sample_term.id, amount=100,
        payment_method="cash", reference_no="REF-PARTIAL", recorded_by=bursar_user.id,
    )
    assert get_balance(sample_student.id, sample_term.id) == 200


# ---------------------------------------------------------------------
# TC03 - Zero payment (BVA lower boundary)
# ---------------------------------------------------------------------
def test_zero_payment_is_rejected(app, sample_student, sample_term, fee_structure, bursar_user):
    with pytest.raises(ps.PaymentError, match="greater than zero"):
        ps.record_payment(
            student_id=sample_student.id, term_id=sample_term.id, amount=0,
            payment_method="cash", reference_no="REF-ZERO", recorded_by=bursar_user.id,
        )


# ---------------------------------------------------------------------
# TC04 - Overpayment (amount > balance)
# ---------------------------------------------------------------------
def test_overpayment_is_rejected_by_default(app, sample_student, sample_term, fee_structure, bursar_user):
    with pytest.raises(ps.PaymentError, match="exceeds outstanding balance"):
        ps.record_payment(
            student_id=sample_student.id, term_id=sample_term.id, amount=1000,
            payment_method="cash", reference_no="REF-OVER", recorded_by=bursar_user.id,
        )


def test_overpayment_allowed_when_explicitly_flagged(app, sample_student, sample_term, fee_structure, bursar_user):
    payment = ps.record_payment(
        student_id=sample_student.id, term_id=sample_term.id, amount=1000,
        payment_method="cash", reference_no="REF-OVER-ALLOWED", recorded_by=bursar_user.id,
        allow_overpayment=True,
    )
    assert payment.amount == 1000


# ---------------------------------------------------------------------
# TC05 - Negative payment (BVA below lower boundary)
# ---------------------------------------------------------------------
def test_negative_payment_is_rejected(app, sample_student, sample_term, fee_structure, bursar_user):
    with pytest.raises(ps.PaymentError, match="greater than zero"):
        ps.record_payment(
            student_id=sample_student.id, term_id=sample_term.id, amount=-50,
            payment_method="cash", reference_no="REF-NEG", recorded_by=bursar_user.id,
        )


# ---------------------------------------------------------------------
# TC06 - Duplicate transaction reference
# ---------------------------------------------------------------------
def test_duplicate_reference_number_is_rejected(app, sample_student, sample_term, fee_structure, bursar_user):
    ps.record_payment(
        student_id=sample_student.id, term_id=sample_term.id, amount=50,
        payment_method="cash", reference_no="REF-DUP", recorded_by=bursar_user.id,
    )
    with pytest.raises(ps.PaymentError, match="Duplicate transaction"):
        ps.record_payment(
            student_id=sample_student.id, term_id=sample_term.id, amount=50,
            payment_method="cash", reference_no="REF-DUP", recorded_by=bursar_user.id,
        )


# ---------------------------------------------------------------------
# TC07 - Invalid student
# ---------------------------------------------------------------------
def test_payment_for_invalid_student_is_rejected(app, sample_term, bursar_user):
    with pytest.raises(ps.PaymentError, match="Invalid student"):
        ps.record_payment(
            student_id=99999, term_id=sample_term.id, amount=50,
            payment_method="cash", reference_no="REF-INVALID-STUDENT", recorded_by=bursar_user.id,
        )


# ---------------------------------------------------------------------
# TC08 - Unauthorized transaction editing (decision table: role x action)
# ---------------------------------------------------------------------
def test_bursar_cannot_edit_payment(app, sample_student, sample_term, fee_structure, bursar_user):
    payment = ps.record_payment(
        student_id=sample_student.id, term_id=sample_term.id, amount=100,
        payment_method="cash", reference_no="REF-EDIT-1", recorded_by=bursar_user.id,
    )
    with pytest.raises(ps.UnauthorizedError, match="Unauthorized"):
        ps.edit_payment(payment.id, editor=bursar_user, new_amount=150)


def test_admin_can_edit_payment_and_audit_log_is_written(app, sample_student, sample_term, fee_structure,
                                                            bursar_user, admin_user):
    from app.models import AuditLog
    payment = ps.record_payment(
        student_id=sample_student.id, term_id=sample_term.id, amount=100,
        payment_method="cash", reference_no="REF-EDIT-2", recorded_by=bursar_user.id,
    )
    updated = ps.edit_payment(payment.id, editor=admin_user, new_amount=150, reason="correction")
    assert updated.amount == 150

    log_entries = AuditLog.query.filter_by(record_id=payment.id, action="EDIT_PAYMENT").all()
    assert len(log_entries) == 1


def test_bursar_cannot_delete_payment(app, sample_student, sample_term, fee_structure, bursar_user):
    payment = ps.record_payment(
        student_id=sample_student.id, term_id=sample_term.id, amount=100,
        payment_method="cash", reference_no="REF-DEL-1", recorded_by=bursar_user.id,
    )
    with pytest.raises(ps.UnauthorizedError):
        ps.delete_payment(payment.id, editor=bursar_user)


# ---------------------------------------------------------------------
# Additional EP case: missing/empty reference number
# ---------------------------------------------------------------------
def test_empty_reference_number_is_rejected(app, sample_student, sample_term, fee_structure, bursar_user):
    with pytest.raises(ps.PaymentError, match="Reference number is required"):
        ps.record_payment(
            student_id=sample_student.id, term_id=sample_term.id, amount=50,
            payment_method="cash", reference_no="   ", recorded_by=bursar_user.id,
        )
