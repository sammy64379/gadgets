"""
Quick script to set all item prices to 10 for M-Pesa Daraja testing.
Run this from the project root directory.
"""

from app import app
from app.db_models import Item, db


def set_prices_to_10():
    """Set all item prices to 10 for testing"""
    with app.app_context():
        items = Item.query.all()
        updated = 0
        for item in items:
            item.price = 10.0
            updated += 1
        db.session.commit()
        print(f"✅ Updated {updated} items to KES 10 for testing")
        print(
            "💡 To restore original prices, check your database backup or seed_items.py"
        )


if __name__ == "__main__":
    set_prices_to_10()
