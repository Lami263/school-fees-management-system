"""
Unit tests for app/services/fee_service.py

Technique coverage:
- Equivalence Partitioning: student with fees / without fees / invalid student
- Boundary Value Analysis: discount == total fees, discount > total fees
"""
import pytest
from app.services import fee_service


def test_total_fees_sums_fee_structure_for_student_class(app, sample_student, sample_term, fee_structure):
    total = fee_service.get_total_fees(sample_student.id, sample_term.id)
    assert total == 300


def test_total_fees_zero_when_no_fee_structure_defined(app, sample_student, sample_term):
    total = fee_service.get_total_fees(sample_student.id, sample_term.id)
    assert total == 0


def test_total_fees_raises_for_invalid_student(app, sample_term):
    with pytest.raises(ValueError, match="Invalid student"):
        fee_service.get_total_fees(9999, sample_term.id)


def test_net_fees_equals_total_fees_when_no_discount(app, sample_student, sample_term, fee_structure):
    net = fee_service.get_net_fees(sample_student.id, sample_term.id)
    assert net == 300


def test_net_fees_boundary_discount_equal_to_total_fees(app, sample_student, sample_term, fee_structure, admin_user):
    """BVA: discount == total_fees -> net fees should be exactly 0, not negative."""
    from app.extensions import db
    from app.models import Discount
    d = Discount(student_id=sample_student.id, term_id=sample_term.id,
                 discount_type="scholarship", amount=300, approved_by=admin_user.id)
    db.session.add(d)
    db.session.commit()

    net = fee_service.get_net_fees(sample_student.id, sample_term.id)
    assert net == 0


def test_net_fees_boundary_discount_exceeds_total_fees(app, sample_student, sample_term, fee_structure, admin_user):
    """BVA edge case: discount > total_fees -> net fees floored at 0, never negative."""
    from app.extensions import db
    from app.models import Discount
    d = Discount(student_id=sample_student.id, term_id=sample_term.id,
                 discount_type="scholarship", amount=500, approved_by=admin_user.id)
    db.session.add(d)
    db.session.commit()

    net = fee_service.get_net_fees(sample_student.id, sample_term.id)
    assert net == 0


def test_balance_equals_net_fees_when_no_payments(app, sample_student, sample_term, fee_structure):
    balance = fee_service.get_balance(sample_student.id, sample_term.id)
    assert balance == 300


def test_student_fee_summary_status_outstanding_vs_fully_paid(app, sample_student, sample_term, fee_structure):
    summary = fee_service.get_student_fee_summary(sample_student.id, sample_term.id)
    assert summary["status"] == "outstanding"
    assert summary["balance"] == 300
