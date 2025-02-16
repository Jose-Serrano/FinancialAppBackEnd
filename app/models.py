from app.services import db
import bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id : int = db.Column(db.Integer, primary_key=True)
    name : str = db.Column(db.String(128), unique=False, nullable=False)
    email : str = db.Column(db.String(128), unique=True, nullable=False)
    hashed_password : str = db.Column(db.String(128), nullable=False)
    balance : float = db.Column(db.Float, default=0)

    alert = db.relationship('Alert', cascade='all,delete', backref='user', lazy=True)
    recurring_expense = db.relationship('RecurringExpense', cascade='all,delete', backref='user', lazy=True)
    transaction = db.relationship('Transaction', cascade='all,delete', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'
    
    def log_in(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
    
    def hash_password(self):
        self.hashed_password = bcrypt.hashpw(self.hashed_password.encode('utf-8'), bcrypt.gensalt())
        return self.hashed_password
    
    def serialize(self):
        return {
            'name': self.name,
            'hashedPassword': self.hashed_password,
            'email': self.email,
        }
    
class Alert(db.Model):
    __tablename__ = 'alerts'
    id : int = db.Column(db.Integer, primary_key=True)
    user_id : int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_amount : float = db.Column(db.Float, nullable=True)
    alert_threshold : float = db.Column(db.Float, nullable=True)
    balance_drop_threshold : float = db.Column(db.Float, nullable=True)
    created_at : str = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Alert {self.id}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_amount': self.target_amount,
            'alert_threshold': self.alert_threshold,
            'balance_drop_threshold': self.balance_drop_threshold
        }
    
    def serialize_threshold(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_amount': self.target_amount,
            'alert_threshold': self.alert_threshold
        }
    
    def serialize_drop(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance_drop_threshold': self.balance_drop_threshold
        }

class RecurringExpense(db.Model):
    __tablename__ = 'recurring_expenses'
    id : int = db.Column(db.Integer, primary_key=True)
    user_id : int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expense_name : str = db.Column(db.String(255), nullable=False)
    amount : float = db.Column(db.Float, nullable=False)
    frequency : str = db.Column(db.String(50), nullable=False)
    start_date : str = db.Column(db.DateTime, nullable=False)
    created_at : str = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<RecurringExpense {self.id}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expense_name': self.expense_name,
            'amount': self.amount,
            'frequency': self.frequency,
            'start_date': self.start_date,
            'created_at': self.created_at
        }
    
    def get_pretty_print(self):
        return {
            'id': self.id,
            'expense_name': self.expense_name,
            'amount': self.amount,
            'frequency': self.frequency,
            'start_date': self.start_date,
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id : int = db.Column(db.Integer, primary_key=True)
    user_id : int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount : float = db.Column(db.Float, nullable=False)
    category : str = db.Column(db.String(255), nullable=False)
    timestamp : datetime = db.Column(db.DateTime, server_default=db.func.now())
    fraud : bool = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Transaction {self.id}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'category': self.category,
            'timestamp': self.timestamp,
            'fraud': self.fraud
        }
    
class Fee(db.Model):
    __tablename__ = 'fees'
    id : int = db.Column(db.Integer, primary_key=True)
    currency_from: str = db.Column(db.String(3), nullable=False)
    currency_to: str = db.Column(db.String(3), nullable=False)
    fee : float = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Fee {self.id} {self.currency_from} {self.currency_to} {self.fee}>'
    
class Rate(db.Model):
    __tablename__ = 'rates'
    id : int = db.Column(db.Integer, primary_key=True)
    currency_from: str = db.Column(db.String(3), nullable=False)
    currency_to: str = db.Column(db.String(3), nullable=False)
    rate : float = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Rate {self.id} {self.currency_from} {self.currency_to} {self.rate}>'
