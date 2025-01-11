from src.db.models import create_schema
from src.db.populate_db import populate_anime_with_favorites
if __name__ == "__main__":
    # Create the database schema
    create_schema()

    # Populate the database
    populate_anime_with_favorites(min_favorites=1)