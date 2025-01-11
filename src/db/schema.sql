CREATE TABLE IF NOT EXISTS Anime (
    anime_id INT PRIMARY KEY,
    title_english VARCHAR(255),
    title_romaji VARCHAR(255),
    description TEXT,
    episodes INT,
    average_score FLOAT,
    favourites INT,
    cover_image_large TEXT,                   -- URL for the large cover image
    cover_image_medium TEXT,
    url TEXT,
    relations TEXT,
    genres TEXT
);

CREATE TABLE IF NOT EXISTS Genres (
    genre_id SERIAL PRIMARY KEY,
    anime_id INT REFERENCES Anime(anime_id),
    genre_name VARCHAR(50)
);



CREATE TABLE IF NOT EXISTS Users(
    user_id INT PRIMARY KEY,
    username VARCHAR(100),
    avatar_url TEXT
);


CREATE TABLE  IF NOT EXISTS UserAnime(
    user_anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES Users(user_id) ON DELETE CASCADE, -- Relate to Users
    anime_id INTEGER REFERENCES Anime(anime_id),
    rating FLOAT,
    favourites BOOLEAN,  
    status VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, anime_id)  -- Add the UNIQUE constraint
);
