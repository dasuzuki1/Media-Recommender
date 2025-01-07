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