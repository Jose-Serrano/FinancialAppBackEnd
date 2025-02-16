from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import Alert
from datetime import datetime
from app.services import db

alerts_blp = Blueprint('alerts', __name__)

@alerts_blp.route('/amount_reached', methods=['POST'])
@jwt_required()
def set_amount_reached_alert():
    if not request.is_json:
        return "Missing JSON in request.", 400
    alert_data = request.get_json()
    if not alert_data or not alert_data['target_amount'] or not alert_data['alert_threshold']:
        return jsonify({"msg": "No empty fields allowed."}), 400
    alert_data['user_id'] = get_jwt_identity()
    alert_data['created_at'] = datetime.now()
    alert = Alert(**alert_data)
    try:
        db.session.add(alert)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'msg': 'error creating the alert'}), 500
    return jsonify({
                    "msg": "Correctly added savings alert!", 
                    "data": alert.serialize_threshold()
                    }), 201

@alerts_blp.route('/balance_drop', methods=['POST'])
@jwt_required()
def set_balance_drop_alert():
    if not request.is_json:
        return "Missing JSON in request.", 400
    alert_data = request.get_json()
    if not alert_data or not alert_data['balance_drop_threshold']:
        return jsonify({"msg": "No empty fields allowed."}), 400
    alert_data['user_id'] = get_jwt_identity()
    alert_data['created_at'] = datetime.now()
    alert = Alert(**alert_data)
    try:
        db.session.add(alert)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'msg': 'error creating the drop alert'}), 500
    return jsonify({"msg": "Correctly added savings alert!",
                    "data": alert.serialize_drop()
                    }), 201

@alerts_blp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_alert():
    if not request.is_json:
        return "Missing JSON in request.", 400
    alert_data = request.get_json()
    if not alert_data:
        return jsonify({"msg": "No empty fields allowed."}), 400
    
    if not alert_data['alert_id']:
        return jsonify({'msg': 'Missing alert ID.'}), 400
    
    alert = Alert.query.filter_by(id=alert_data['alert_id']).first()
    if not alert:
        return jsonify({'msg': 'Alert not found.'}), 404
    
    if alert.user_id != get_jwt_identity():
        return jsonify({'msg': 'unauthorized'}), 401
    try:
        db.session.delete(alert)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'msg': 'error deleting the alert'}), 500
    return jsonify({'msg': 'alert deleted'}), 200

@alerts_blp.route('/list', methods=['GET'])
@jwt_required()
def get_user_alerts():
    user_id = get_jwt_identity()
    alerts = Alert.query.filter_by(user_id=user_id).all()
    return jsonify({"data":[alert.serialize() for alert in alerts]}), 200