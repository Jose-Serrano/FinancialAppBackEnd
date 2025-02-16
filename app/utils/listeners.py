from sqlalchemy import event
from sqlalchemy.orm import Session
from app.services import db
from app.services import EmailManager
from app.models import Transaction, User, Alert
from flask import g

@event.listens_for(db.session.__class__, "before_flush")
def session_commited(session, flush_context, instances):
    for instance in session.new:
        if isinstance(instance, Transaction):
            user : User = User.query.get(instance.user_id)
            user.balance += instance.amount
            if user.balance < 0:
                session.rollback()
                raise Exception('Insufficient funds')
            
    for instance in session.dirty:
        if isinstance(instance, Transaction):
            user : User = User.query.get(instance.user_id)
            user.balance += instance.amount
            if user.balance < 0:
                session.rollback()
                raise Exception('Insufficient funds')
    g.trigger_email = True
            
@event.listens_for(User, "after_update")
def generate_alert(mapper, connection, target : User):
    if getattr(g, 'trigger_email', False):
        balance = target.balance
        alerts = Alert.query.filter_by(user_id=target.id).all()
        for alert in alerts:
            if alert.balance_drop_threshold and balance < alert.balance_drop_threshold:
                EmailManager.send_email(target, 'email/dropalert.html',alert.balance_drop_threshold)
            elif alert.alert_threshold and alert.target_amount and balance > alert.alert_threshold and balance < alert.target_amount:
                EmailManager.send_email(target,'email/savingalert.html', alert.target_amount)
        g.trigger_email = False
