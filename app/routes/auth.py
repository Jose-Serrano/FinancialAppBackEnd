from flask import Blueprint, request, jsonify
from app.services.servicesManager import db
from app.models import User
from flask_jwt_extended import create_access_token
from app.utils import Mail_Validator

auth_blp = Blueprint('auth', __name__)

@auth_blp.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return "Missing JSON in request.", 400
    register_data = request.get_json()
    if "password" not in register_data or "email" not in register_data or "name" not in register_data:
        return "All fields are required.", 400
    
    if register_data['name'] == '' or register_data['email'] == '' or register_data['password'] == '':
        return "No empty fields allowed.", 400

    register_data['hashed_password'] = register_data.pop('password')

    new_user = User(**register_data)
    new_user.hash_password()

    if not Mail_Validator.valid_email(new_user.email):
        return f"Invalid email: {new_user.email}", 400

    if User.query.filter_by(email=new_user.email).first():
        return "Email already exists.", 400

    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'msg': 'error creating the user'}), 500
    return jsonify(new_user.serialize()), 201

@auth_blp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return "Missing JSON in request.", 400
    login_data = request.get_json()

    if not login_data or not login_data['email'] or not login_data['password']:
        return "Bad credentials.", 401
    
    if not Mail_Validator.valid_email(login_data['email']):
        return f"Invalid email: {login_data['email']}", 400
    
    user = User.query.filter_by(email=login_data['email']).first()
    if not user:
        return f'User not found for the given email: {login_data["email"]}', 400
    if not user.log_in(login_data['password']):
        return "Bad credentials.", 401
    access_token = create_access_token(identity=user.id)
    return jsonify({'token': access_token}),201