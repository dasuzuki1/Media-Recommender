import sqlite3

def create_schema(db_path="data/anilist.db"):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read schema from the file
    with open("src/db/schema.sql", "r") as file:
        schema = file.read()

    # Execute schema
    cursor.executescript(schema)
    conn.commit()
    conn.close()

    print("Database schema created successfully!")
