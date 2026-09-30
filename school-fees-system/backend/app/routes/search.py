from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Student

search_bp = Blueprint("search", __name__)


@search_bp.get("/students")
@jwt_required()
def search_students():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    like = f"%{q}%"
    students = Student.query.filter(
        (Student.first_name.ilike(like)) |
        (Student.last_name.ilike(like)) |
        (Student.admission_no.ilike(like))
    ).all()
    return jsonify([s.to_dict() for s in students])
