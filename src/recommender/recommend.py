#Using Cosine Similarity Algorithm

import sqlite3
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer,MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

#Connect to the database
conn = sqlite3.connect("data/anilist.db")

#Query anime data for important columns


anime_query = """
SELECT anime_id, title_romaji, genres, average_score
FROM Anime;
"""

anime_df = pd.read_sql_query(anime_query, conn)

user_id = 1
user_query = """
SELECT anime_id, rating, favourites
FROM userAnime
WHERE user_id = ?;

"""

user_df = pd.read_sql_query(user_query,conn,params=(user_id,))

anime_df['genres'] = anime_df['genres'].str.split(', ')
mlb = MultiLabelBinarizer()
genre_vector = mlb.fit_transform(anime_df['genres'])

genre_df = pd.DataFrame(genre_vector, columns = mlb.classes_, index=anime_df.index)
anime_df = pd.concat([anime_df, genre_df], axis = 1)


scaler = MinMaxScaler()
anime_df[['average_score', 'favourites']] = scaler.fit_transform(anime_df[['average_score', 'favourites']])


user_anime_df = user_df.merge(anime_df, on='anime_id', how='inner')

user_genre_weights = user_anime_df[mlb.classes_].T.dot(user_anime_df['rating'])

user_genre_weights /= user_genre_weights.sum()

user_vector = pd.concat([
    user_genre_weights,
    pd.Series([user_anime_df['average_score'].mean(), user_anime_df['favourite'].mean()], index=['average_score', 'favorites'])
])

anime_vectors = anime_df[mlb.classes_ + ['average_score', 'favourites']].values

similarity_scores = cosine_similarity([user_vector], anime_vectors)[0]

anime_df['similarity_score'] = similarity_scores

recommendations = anime_df[~anime_df['anime_id'].isin(user_df['anime_id'])]

recommendations = recommendations.sort_values(by='similarity_score', ascending=False)

top_n = 10
print(recommendations[['title_romaji','similarity_score']].head(top_n))