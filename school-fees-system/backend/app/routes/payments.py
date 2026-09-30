from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Payment, User
from app.routes.utils import role_required
from app.services.payment_service import (
    record_payment,
    edit_payment,
    delete_payment,
    PaymentError,
    UnauthorizedError,
)

payments_bp = Blueprint("payments", __name__)


@payments_bp.get("")
@jwt_required()
def list_payments():
    student_id = request.args.get("student_id", type=int)
    term_id = request.args.get("term_id", type=int)
    query = Payment.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if term_id:
        query = query.filter_by(term_id=term_id)
    payments = query.order_by(Payment.created_at.desc()).all()
    return jsonify([p.to_dict() for p in payments])


@payments_bp.post("")
@role_required("admin", "bursar")
def create_payment():
    data = request.get_json() or {}
    required = ["student_id", "term_id", "amount", "payment_method", "reference_no"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"missing required fields: {', '.join(missing)}"}), 400

    recorded_by = int(get_jwt_identity())
    try:
        payment = record_payment(
            student_id=data["student_id"],
            term_id=data["term_id"],
            amount=data["amount"],
            payment_method=data["payment_method"],
            reference_no=data["reference_no"],
            recorded_by=recorded_by,
            allow_overpayment=bool(data.get("allow_overpayment", False)),
        )
    except PaymentError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(payment.to_dict()), 201


@payments_bp.put("/<int:payment_id>")
@role_required("admin")
def update_payment(payment_id):
    data = request.get_json() or {}
    editor_id = int(get_jwt_identity())
    editor = User.query.get(editor_id)

    try:
        payment = edit_payment(
            payment_id=payment_id,
            editor=editor,
            new_amount=data.get("amount"),
            new_status=data.get("status"),
            reason=data.get("reason", ""),
        )
    except UnauthorizedError as e:
        return jsonify({"error": str(e)}), 403
    except PaymentError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(payment.to_dict())


@payments_bp.delete("/<int:payment_id>")
@role_required("admin")
def remove_payment(payment_id):
    editor_id = int(get_jwt_identity())
    editor = User.query.get(editor_id)
    try:
        delete_payment(payment_id, editor, reason=request.args.get("reason", ""))
    except UnauthorizedError as e:
        return jsonify({"error": str(e)}), 403
    except PaymentError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "payment reversed"})
