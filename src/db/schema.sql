CREATE TABLE Anime (
    anime_id INT PRIMARY KEY,
    title_english VARCHAR(255),
    title_romaji VARCHAR(255),
    description TEXT,
    episodes INT,
    average_score FLOAT,
    genres TEXT -- Comma-separated genres (optional normalization)
);

CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    anime_id INT REFERENCES Anime(anime_id),
    genre_name VARCHAR(50)
);



CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(100),
    avatar_url TEXT
);


CREATE TABLE UserAnime (
    user_anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES Users(user_id) ON DELETE CASCADE, -- Relate to Users
    anime_id INTEGER REFERENCES Anime(anime_id),
    rating FLOAT,
    favorite BOOLEAN,  
    status VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, anime_id)  -- Add the UNIQUE constraint
);

