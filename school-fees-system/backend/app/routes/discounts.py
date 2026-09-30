from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Discount, Student
from app.routes.utils import role_required

discounts_bp = Blueprint("discounts", __name__)


@discounts_bp.get("")
@jwt_required()
def list_discounts():
    student_id = request.args.get("student_id", type=int)
    term_id = request.args.get("term_id", type=int)
    query = Discount.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if term_id:
        query = query.filter_by(term_id=term_id)
    return jsonify([d.to_dict() for d in query.all()])


@discounts_bp.post("")
@role_required("admin", "bursar")
def create_discount():
    data = request.get_json() or {}
    required = ["student_id", "term_id", "discount_type", "amount"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"missing required fields: {', '.join(missing)}"}), 400

    if Student.query.get(data["student_id"]) is None:
        return jsonify({"error": "invalid student"}), 400

    if float(data["amount"]) < 0:
        return jsonify({"error": "discount amount cannot be negative"}), 400

    approver_id = get_jwt_identity()
    d = Discount(
        student_id=data["student_id"],
        term_id=data["term_id"],
        discount_type=data["discount_type"],
        amount=data["amount"],
        reason=data.get("reason", ""),
        approved_by=int(approver_id),
    )
    db.session.add(d)
    db.session.commit()
    return jsonify(d.to_dict()), 201


@discounts_bp.delete("/<int:discount_id>")
@role_required("admin")
def delete_discount(discount_id):
    d = Discount.query.get(discount_id)
    if d is None:
        return jsonify({"error": "discount not found"}), 404
    db.session.delete(d)
    db.session.commit()
    return jsonify({"message": "discount deleted"})
