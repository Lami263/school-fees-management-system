from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import FeeStructure
from app.routes.utils import role_required

fees_bp = Blueprint("fees", __name__)


@fees_bp.get("")
@jwt_required()
def list_fee_structures():
    class_id = request.args.get("class_id", type=int)
    term_id = request.args.get("term_id", type=int)
    query = FeeStructure.query
    if class_id:
        query = query.filter_by(class_id=class_id)
    if term_id:
        query = query.filter_by(term_id=term_id)
    return jsonify([f.to_dict() for f in query.all()])


@fees_bp.post("")
@role_required("admin")
def create_fee_structure():
    data = request.get_json() or {}
    required = ["class_id", "term_id", "fee_type", "amount"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"missing required fields: {', '.join(missing)}"}), 400

    if float(data["amount"]) < 0:
        return jsonify({"error": "amount cannot be negative"}), 400

    fs = FeeStructure(
        class_id=data["class_id"],
        term_id=data["term_id"],
        fee_type=data["fee_type"],
        amount=data["amount"],
    )
    db.session.add(fs)
    db.session.commit()
    return jsonify(fs.to_dict()), 201


@fees_bp.put("/<int:fee_id>")
@role_required("admin")
def update_fee_structure(fee_id):
    fs = FeeStructure.query.get(fee_id)
    if fs is None:
        return jsonify({"error": "fee structure not found"}), 404
    data = request.get_json() or {}
    if "amount" in data:
        if float(data["amount"]) < 0:
            return jsonify({"error": "amount cannot be negative"}), 400
        fs.amount = data["amount"]
    if "fee_type" in data:
        fs.fee_type = data["fee_type"]
    db.session.commit()
    return jsonify(fs.to_dict())


@fees_bp.delete("/<int:fee_id>")
@role_required("admin")
def delete_fee_structure(fee_id):
    fs = FeeStructure.query.get(fee_id)
    if fs is None:
        return jsonify({"error": "fee structure not found"}), 404
    db.session.delete(fs)
    db.session.commit()
    return jsonify({"message": "fee structure deleted"})
