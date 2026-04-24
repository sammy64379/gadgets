from app import app
from app.db_models import db

with app.app_context():
    db.drop_all()
    db.create_all()

print("Database reset successful")