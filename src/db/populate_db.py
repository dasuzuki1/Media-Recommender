import sqlite3
from src.api.fetch_data import fetch_anime_by_title, fetch_popular_anime, fetch_anime_with_favorites
import time
import json
def populate_database():
    """
    Fetch popular anime and populate the database.
    """
    # Connect to the database
    conn = sqlite3.connect("data/anilist.db")

    # Fetch popular anime
    popular_anime = fetch_popular_anime(page=1, per_page=100)

    # Insert anime into the database
    for anime in popular_anime:
        print(anime)
        insert_anime(conn, anime)

    conn.close()
    print("Database populated with popular anime!")


def populate_anime_with_favorites(min_favorites=50):
    # Connect to the database
    conn = sqlite3.connect("data/anilist.db")
    cursor = conn.cursor()

    # Pagination variables
    page = 1
    per_page = 50
    total_fetched = 0

    while True:
        # Fetch anime from AniList API
        anime_list = fetch_anime_with_favorites(min_favorites=min_favorites, page=page, per_page=per_page)

        if not anime_list:  # Exit loop if no more data
            break

        # Insert fetched anime into the database
        for anime in anime_list:
            relations = anime.get("relations", {}).get("edges", [])
            relations_json = json.dumps([{
                "relationType": edge.get("relationType", "UNKNOWN"),
                "relatedAnimeId": edge.get("node", {}).get("id")
            } for edge in relations])
            print(relations_json)
            cursor.execute("""
            INSERT OR IGNORE INTO Anime (anime_id, title_romaji, title_english, description, episodes, average_score, favourites, relations, genres)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                anime["id"],
                anime.get("title", {}).get("romaji", "Unknown Title"),
                anime.get("title", {}).get("english", "Unknown Title"),
                anime.get("description", "No description available."),
                anime.get("episodes", 0),
                anime.get("averageScore", 0),
                anime.get("favourites", 0),
                relations_json,  # Ensure this is a string
                ", ".join(anime.get("genres", []))
            ))

            total_fetched += 1

        # Commit after each page
        conn.commit()

        # Move to the next page
        print(f"Page {page} processed.")
        page += 1
        time.sleep(2)
        

    # Close the database connection
    conn.close()
    print(f"Database populated with {total_fetched} anime with more than {min_favorites} favorites.")

def insert_anime(conn, anime):
    cursor = conn.cursor()

    # Insert into Anime table
    cursor.execute("""
    INSERT OR IGNORE INTO Anime (anime_id, title_romaji, title_english, description, episodes, average_score, genres)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        anime["id"],
        anime["title"]["romaji"],
        anime["title"]["english"],
        anime["description"],
        anime["episodes"],
        anime["averageScore"],
        ", ".join(anime["genres"])
    ))

    # Insert genres into Genres table (optional)
    for genre in anime["genres"]:
        cursor.execute("""
        INSERT INTO Genres (anime_id, genre_name)
        VALUES (?, ?)
        """, (anime["id"], genre))

    conn.commit()

import os
import sqlite3

def initialize_useranime_database():
    conn = sqlite3.connect("data/anilist.db")
    cursor = conn.cursor()

    # Create Anime table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Anime (
        anime_id INTEGER PRIMARY KEY,
        title_romaji VARCHAR(255),
        title_english VARCHAR(255),
        description TEXT,
        episodes INTEGER,
        average_score FLOAT,
        genres TEXT
    );
    """)

    # Create UserAnime table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserAnime (
        user_anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        anime_id INTEGER REFERENCES Anime(anime_id),
        rating FLOAT,
        favourites BOOLEAN,
        status VARCHAR(20),
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, anime_id)
    );
    """)

    conn.commit()
    conn.close()

# Call this function in your app
