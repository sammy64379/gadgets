from app import app
from app.db_models import Item


def main():
    with app.app_context():
        items = Item.query.order_by(Item.category, Item.name).all()
        print(f"Existing items: {len(items)}")
        for item in items:
            print(
                f"{item.id:>3} | {item.category:<12} | {item.name:<45} | KES {item.price:,.0f}"
            )


if __name__ == "__main__":
    main()
