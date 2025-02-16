from app.models import Fee, Transaction, Rate
from sqlalchemy import func
from app.services import db
from datetime import timedelta
import numpy as np
from email_validator import validate_email, EmailNotValidError

class Mail_Validator:        
    @staticmethod
    def valid_email(email):
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

class Calculator:
    @staticmethod
    def calculate_fee(amount: float, source_ccy: str, target_ccy: str) -> float:
        fee : Fee = Fee.query.filter_by(currency_from=source_ccy, currency_to=target_ccy).first()
        rate : Rate = Rate.query.filter_by(currency_from=source_ccy, currency_to=target_ccy).first()
        if fee:
            return amount*(1-fee.fee)*rate.rate
        return None

    @staticmethod
    def evaluate_transaction(transaction: Transaction) -> bool:
        return Calculator._deviation_from_average(transaction) or Calculator._unusal_spending_category(transaction) or Calculator._unusual_transactions_amount(transaction)

    @staticmethod
    def _deviation_from_average(transaction: Transaction) -> bool:
        min_days = transaction.timestamp - timedelta(days=90)
        average_spending_90_days_list = db.session.query(func.sum(Transaction.amount))\
                                        .filter(Transaction.user_id == transaction.user_id, Transaction.timestamp >= min_days)\
                                        .group_by(func.date(Transaction.timestamp)).all()
        if not average_spending_90_days_list:
            return False
        
        average_spending_mean = np.average([i[0] for i in average_spending_90_days_list])
        average_spending_std = np.std([i[0] for i in average_spending_90_days_list])

        if transaction.amount > average_spending_mean + 3*average_spending_std:
            return True
        
        return False
    
    @staticmethod
    def _unusal_spending_category(transaction: Transaction) -> bool:
        categories = Transaction.query.with_entities(Transaction.category).filter_by(user_id=transaction.user_id).distinct().all()
        categories = [category[0] for category in categories]
        return transaction.category not in categories
    
    @staticmethod
    def _unusual_transactions_amount(transaction: Transaction) -> bool:
        min_time = transaction.timestamp - timedelta(minutes=5)
        count = Transaction.query.with_entities(func.count(Transaction.id)).filter(Transaction.timestamp >= min_time, Transaction.user_id==transaction.user_id).scalar()
        return count > 5
