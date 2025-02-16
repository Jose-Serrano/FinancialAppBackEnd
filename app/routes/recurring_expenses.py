from flask import Blueprint, request, jsonify
from app.services.servicesManager import jwt, db
from app.models import RecurringExpense
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from dateutil.relativedelta import relativedelta

recurring_expenses_blp = Blueprint('recurring_expenses', __name__)

@recurring_expenses_blp.route('/', methods=['POST'])
@jwt_required()
def create_recurring_expense():
    if not request.is_json:
        return "Missing JSON in request.", 400
    recurring_expense_data = request.get_json()
    if not recurring_expense_data or "expense_name" not in recurring_expense_data or "amount" not in recurring_expense_data or "frequency" not in recurring_expense_data or "start_date" not in recurring_expense_data:
        return jsonify({'msg': 'No data provided.'}), 400
    elif not recurring_expense_data['expense_name'] or not recurring_expense_data['amount'] or not recurring_expense_data['frequency'] or not recurring_expense_data['start_date']:
        return jsonify({'msg': 'No empty fields allowed.'}), 400
    recurring_expense_data['user_id'] = get_jwt_identity()
    recurring_expense_data['created_at'] = datetime.now()
    new_recurring_expense = RecurringExpense(**recurring_expense_data)
    try:
        db.session.add(new_recurring_expense)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'msg': 'error creating the recurring expense'}), 500
    return jsonify({'msg': "Recurring expense added successfully.",
                    "data": new_recurring_expense.get_pretty_print()
                    }), 201

@recurring_expenses_blp.route('/', methods=['GET'])
@jwt_required()
def get_recurring_expenses():
    user_id = get_jwt_identity()
    recurring_expenses = RecurringExpense.query.filter_by(user_id=user_id).all()
    return [recurring_expense.serialize() for recurring_expense in recurring_expenses], 200

@recurring_expenses_blp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_expense(id):
    if not request.is_json:
        return "Missing JSON in request.", 400
    expense_data = request.get_json()
    if not expense_data or "expense_name" not in expense_data or "amount" not in expense_data or "frequency" not in expense_data or "start_date" not in expense_data:
        return jsonify({'msg': 'No data provided.'}), 400
    elif expense_data['expense_name'] == '' or expense_data['amount'] == '' or expense_data['frequency'] == '' or expense_data['start_date'] == '':
        return jsonify({'msg': 'No empty fields allowed.'}), 400
    
    expense : RecurringExpense = RecurringExpense.query.get(id)
    
    if not expense or expense.user_id != get_jwt_identity():
        return jsonify({'msg': 'Expense not found.'}), 404
    
    for key, value in expense_data.items():
        setattr(expense, key, value)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'msg': 'error'}), 400
    return jsonify({'msg': "Recurring expense updated successfully.","data":expense.get_pretty_print()}), 200

@recurring_expenses_blp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    expense : RecurringExpense = RecurringExpense.query.get(id)
    if not expense or expense.user_id != get_jwt_identity():
        return jsonify({'msg': 'Expense not found.'}), 404
    try:
        db.session.delete(expense)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'msg': f"Couldn't delete the expense with id {expense.id}"}), 500
    return jsonify({'msg': "Recurring expense deleted successfully."}), 200

@recurring_expenses_blp.route('/projection', methods=['GET'])
@jwt_required()
def get_projection():
    user_id = get_jwt_identity()
    today = datetime.now()
    recurring_expenses = RecurringExpense.query.filter_by(user_id=user_id).all()
    list_projection = []
    for i in range (1, 13):
        projection = {}
        current_month = today + relativedelta(months=i)
        total_amount = 0
        for expense in recurring_expenses:
            if expense.start_date > today:
                continue
            total_amount += expense.amount
        projection["month"] = current_month.strftime('%y-%m')
        projection["recurring_expenses"] = total_amount
        list_projection.append(projection)
    return f"list of monthly expenses {list_projection}", 200
    