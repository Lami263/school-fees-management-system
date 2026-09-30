from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import ClassRoom, Term
from app.routes.utils import role_required

classes_terms_bp = Blueprint("classes_terms", __name__)


@classes_terms_bp.get("/classes")
@jwt_required()
def list_classes():
    return jsonify([c.to_dict() for c in ClassRoom.query.order_by(ClassRoom.name).all()])


@classes_terms_bp.post("/classes")
@role_required("admin")
def create_class():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    c = ClassRoom(name=data["name"], level=data.get("level"))
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201


@classes_terms_bp.get("/terms")
@jwt_required()
def list_terms():
    return jsonify([t.to_dict() for t in Term.query.order_by(Term.start_date.desc()).all()])


@classes_terms_bp.post("/terms")
@role_required("admin")
def create_term():
    data = request.get_json() or {}
    required = ["name", "academic_year"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"missing required fields: {', '.join(missing)}"}), 400
    t = Term(
        name=data["name"],
        academic_year=data["academic_year"],
        start_date=data.get("start_date") or None,
        end_date=data.get("end_date") or None,
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201
