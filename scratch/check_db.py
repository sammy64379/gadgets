import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))
from app import app
from app.db_models import Item

with app.app_context():
    item = Item.query.filter_by(name='Nutribullet NB9-1212 high-Speed Blender').first()
    if item:
        print(f"ITEM_FOUND_IMAGE: {item.image}")
    else:
        print("ITEM_NOT_FOUND")
