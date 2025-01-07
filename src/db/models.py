import sqlite3

def create_schema():
    conn = sqlite3.connect("data/anilist.db")
    cursor = conn.cursor()

    # Create Anime table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Anime (
        anime_id INT PRIMARY KEY,
        title_romaji VARCHAR(255),
        title_english VARCHAR(255),
        description TEXT,
        episodes INT,
        average_score FLOAT,
        genres TEXT
    )
    """)

    # Create Genres table (if normalizing genres)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Genres (
        genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
        anime_id INT,
        genre_name VARCHAR(50),
        FOREIGN KEY (anime_id) REFERENCES Anime(anime_id)
    )
    """)

    conn.commit()
    conn.close()
