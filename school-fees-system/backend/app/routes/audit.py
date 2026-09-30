from flask import Blueprint, jsonify
from app.models import AuditLog
from app.routes.utils import role_required

audit_bp = Blueprint("audit", __name__)


@audit_bp.get("")
@role_required("admin")
def list_audit_log():
    entries = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    return jsonify([e.to_dict() for e in entries])
