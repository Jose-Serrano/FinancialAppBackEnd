from flask import Flask
from app.services import jwt, db
from .routes import auth_blp, transactions_blp, alerts_blp, recurring_expenses_blp, transfers_blp
#import logging

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@mysql:3306/bankingapp"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jose'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_VERIFY_SUB'] = False
    app.config['SECRET_KEY'] = 'jose'
    jwt.init_app(app)
    db.init_app(app)

    app.register_blueprint(auth_blp, url_prefix='/api/auth')
    app.register_blueprint(recurring_expenses_blp, url_prefix='/api/recurring-expenses')
    app.register_blueprint(transfers_blp, url_prefix='/api/transfers/')
    app.register_blueprint(alerts_blp, url_prefix='/api/alerts')
    app.register_blueprint(transactions_blp, url_prefix='/api/transactions')

    return app