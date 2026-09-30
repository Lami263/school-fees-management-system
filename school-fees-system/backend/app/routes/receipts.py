from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Receipt

receipts_bp = Blueprint("receipts", __name__)


@receipts_bp.get("/<int:payment_id>")
@jwt_required()
def get_receipt(payment_id):
    receipt = Receipt.query.filter_by(payment_id=payment_id).first()
    if receipt is None:
        return jsonify({"error": "receipt not found"}), 404
    data = receipt.to_dict()
    data["payment"] = receipt.payment.to_dict()
    return jsonify(data)
