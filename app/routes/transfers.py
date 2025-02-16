from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils import Calculator
from datetime import datetime
from app.models import Fee, Rate

transfers_blp = Blueprint('transfers', __name__)

@transfers_blp.route('/simulate', methods=['POST'])
@jwt_required()
def simulate_transaction():
    if not request.is_json:
        return "Missing JSON in request.", 400
    transaction_data = request.get_json()
    if not transaction_data['amount'] or not transaction_data['source_currency'] or not transaction_data['target_currency']:
        return jsonify({'msg': 'missing data'}), 400
    transaction_data['user_id'] = get_jwt_identity()
    transaction_data['timestamp'] = datetime.now()
    total_amount = Calculator.calculate_fee(transaction_data['amount'], transaction_data['source_currency'], transaction_data['target_currency'])
    if not total_amount:
        return jsonify({'msg': 'Invalid currencies or no exchange data available.'}), 404
    return jsonify({'msg': f"Amount in target currency: {total_amount}"}), 200

@transfers_blp.route('/fees', methods=['GET'])
@jwt_required()
def get_fees():
    fees = request.args
    source_currency, target_currency = fees.get('source_currency'), fees.get('target_currency')
    if not source_currency or not target_currency:
        return jsonify({'msg': 'No empty fields allowed.'}), 400
    fee = Fee.query.filter_by(currency_from=source_currency, currency_to=target_currency).first()
    if not fee:
        return jsonify({'msg': "No fee information available for these currencies."}), 404
    return jsonify({'fee': fee.fee}), 200

@transfers_blp.route('/rates', methods=['GET'])
@jwt_required()
def get_rates():
    rates = request.args
    source_currency, target_currency = rates.get('source_currency'), rates.get('target_currency')
    if not source_currency or not target_currency:
        return jsonify({'msg': 'No empty fields allowed.'}), 400
    rate = Rate.query.filter_by(currency_from=source_currency, currency_to=target_currency).first()
    if not rate:
        return jsonify({'msg': 'No exchange rate available for these currencies.'}), 404
    return jsonify({'rate': rate.rate}), 200