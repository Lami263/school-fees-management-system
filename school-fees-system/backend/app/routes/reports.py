from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Student, Payment
from app.services.fee_service import get_student_fee_summary

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/student/<int:student_id>/statement")
@jwt_required()
def student_statement(student_id):
    term_id = request.args.get("term_id", type=int)
    if not term_id:
        return jsonify({"error": "term_id is required"}), 400
    try:
        summary = get_student_fee_summary(student_id, term_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    payments = Payment.query.filter_by(student_id=student_id, term_id=term_id).all()
    summary["payments"] = [p.to_dict() for p in payments]
    return jsonify(summary)


@reports_bp.get("/outstanding")
@jwt_required()
def outstanding_report():
    term_id = request.args.get("term_id", type=int)
    if not term_id:
        return jsonify({"error": "term_id is required"}), 400

    students = Student.query.filter_by(status="active").all()
    results = []
    for s in students:
        summary = get_student_fee_summary(s.id, term_id)
        if summary["balance"] > 0:
            results.append({
                "student_id": s.id,
                "admission_no": s.admission_no,
                "name": f"{s.first_name} {s.last_name}",
                "class_name": s.class_room.name if s.class_room else None,
                "balance": summary["balance"],
            })
    results.sort(key=lambda r: r["balance"], reverse=True)
    return jsonify(results)


@reports_bp.get("/collections")
@jwt_required()
def collections_report():
    term_id = request.args.get("term_id", type=int)
    query = Payment.query.filter_by(status="confirmed")
    if term_id:
        query = query.filter_by(term_id=term_id)
    payments = query.all()

    total = sum(float(p.amount) for p in payments)
    by_method = {}
    for p in payments:
        by_method[p.payment_method] = by_method.get(p.payment_method, 0) + float(p.amount)

    return jsonify({
        "total_collected": total,
        "transaction_count": len(payments),
        "by_payment_method": by_method,
    })
