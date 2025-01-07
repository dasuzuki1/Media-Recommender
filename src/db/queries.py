def get_top_anime_by_score(conn, limit=10):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT title_romaji, average_score
    FROM Anime
    ORDER BY average_score DESC
    LIMIT ?
    """, (limit,))
    return cursor.fetchall()
