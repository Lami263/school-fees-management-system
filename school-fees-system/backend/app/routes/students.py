from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Student
from app.routes.utils import role_required

students_bp = Blueprint("students", __name__)


@students_bp.get("")
@jwt_required()
def list_students():
    status = request.args.get("status")
    query = Student.query
    if status:
        query = query.filter_by(status=status)
    students = query.order_by(Student.last_name).all()
    return jsonify([s.to_dict() for s in students])


@students_bp.get("/<int:student_id>")
@jwt_required()
def get_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        return jsonify({"error": "student not found"}), 404
    return jsonify(student.to_dict())


@students_bp.post("")
@role_required("admin", "bursar")
def create_student():
    data = request.get_json() or {}
    required = ["admission_no", "first_name", "last_name"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"missing required fields: {', '.join(missing)}"}), 400

    if Student.query.filter_by(admission_no=data["admission_no"]).first():
        return jsonify({"error": "admission_no already exists"}), 409

    student = Student(
        admission_no=data["admission_no"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        dob=data.get("dob") or None,
        gender=data.get("gender"),
        class_id=data.get("class_id"),
        guardian_name=data.get("guardian_name"),
        guardian_phone=data.get("guardian_phone"),
        status=data.get("status", "active"),
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@students_bp.put("/<int:student_id>")
@role_required("admin", "bursar")
def update_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        return jsonify({"error": "student not found"}), 404

    data = request.get_json() or {}
    for field in ["first_name", "last_name", "dob", "gender", "class_id",
                  "guardian_name", "guardian_phone", "status"]:
        if field in data:
            setattr(student, field, data[field])

    db.session.commit()
    return jsonify(student.to_dict())


@students_bp.delete("/<int:student_id>")
@role_required("admin")
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        return jsonify({"error": "student not found"}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "student deleted"})
