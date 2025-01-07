import sqlite3

def insert_anime(conn, anime):
    cursor = conn.cursor()

    # Insert into Anime table
    cursor.execute("""
    INSERT INTO Anime (anime_id, title_romaji, title_english, description, episodes, average_score, genres)
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
