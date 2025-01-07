from src.api.fetch_data import fetch_anime_by_title, fetch_popular_anime
from src.db.models import create_schema
from src.db.populate_db import insert_anime
import sqlite3

if __name__ == "__main__":
    # Create the database schema
    create_schema()

    # Connect to the database
    conn = sqlite3.connect("data/anilist.db")

    # Fetch popular anime
    popular_anime = fetch_popular_anime()
    for anime in popular_anime:
        insert_anime(conn, anime)

    conn.close()
    print("Database populated with popular anime!")
