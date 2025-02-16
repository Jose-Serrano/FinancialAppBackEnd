from app import create_app
from app.services import db
from app.models import Fee, Rate
import csv 
import logging

flaskApp = create_app()
with flaskApp.app_context():
    db.create_all()


    if not Fee.query.first():
        with open('app/exchange_fees.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            try:
                for row in reader:
                    fee = Fee(**row)
                    db.session.add(fee)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                db.session.flush()
                logging.error(f"Error importing fees from CSV: {e}")
    if not Rate.query.first():
        with open('app/exchange_rates.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            try:
                for row in reader:
                    rate = Rate(**row)
                    db.session.add(rate)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.flush()
                logging.error(f"Error importing rates from CSV: {e}")
            
if __name__ == '__main__':
    flaskApp.run(host='0.0.0.0',port=3000, debug=False)