from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services import db
from app.models import Transaction, User
from datetime import datetime
from app.utils import Calculator

transactions_blp = Blueprint('transactions', __name__)

@transactions_blp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    if not request.is_json:
        return "Missing JSON in request.", 400
    transaction_data = request.get_json()
    if not transaction_data:
        return jsonify({'msg': 'No data provided.'}), 400
    elif not transaction_data['amount'] or not transaction_data['user_id'] or not transaction_data['category']:
        return jsonify({"msg": "No empty fields allowed."}), 400

    user = User.query.get(transaction_data['user_id'])
    if not user:
        return jsonify({'msg': 'user not found'}), 404
    
    if "timestamp" in transaction_data: 
        transaction_data['timestamp'] = datetime.strptime(transaction_data['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    else:
        transaction_data['timestamp'] = datetime.now()

    transaction = Transaction(**transaction_data)
    if Calculator.evaluate_transaction(transaction=transaction):
        transaction.fraud = True
    try:
        db.session.add(transaction)
        db.session.flush()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.commit()
        return jsonify({'msg': repr(e)}), 500
    
    return jsonify({"msg": "Transaction added and evaluated for fraud.",
                    "data": transaction.serialize()}), 201

