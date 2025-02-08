from flask import Flask, request, redirect, session, jsonify, render_template
from src.db.populate_db import initialize_useranime_database
import pip._vendor.requests as requests
import sqlite3
import secrets
import os
import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer,MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)  # Required for session management
initialize_useranime_database()

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
API_HEADERS = {
    "Content-Type": os.getenv("CONTENT_TYPE"),
    "Accept": os.getenv("ACCEPT")
}

def fetch_user_anime_list(access_token):
    url = "https://graphql.anilist.co"

    # Step 1: Fetch the user's ID
    viewer_query = """
    query {
      Viewer {
        id
        name
        avatar {
          large
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(url, json={"query": viewer_query}, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch user ID:", response.status_code, response.text)
        return None

    viewer_data = response.json().get("data", {}).get("Viewer", {})
    user_id = viewer_data.get("id")
    if not user_id:
        print("Failed to retrieve user ID from Viewer data.")
        return None

    # Step 2: Fetch the user's anime list
    anime_list_query = """
    query ($userId: Int) {
      MediaListCollection(userId: $userId, type: ANIME) {
        lists {
          name
          entries {
            media {
              id
              title {
                romaji
                english
              }
              genres
              episodes
              averageScore
            }
            score
            status
            media {
              isFavourite
            }
          }
        }
      }
    }
    """
    variables = {"userId": user_id}
    response = requests.post(url, json={"query": anime_list_query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        return response.json()["data"]["MediaListCollection"]["lists"]
    else:
        print("Failed to fetch user anime list:", response.status_code, response.text)
        return None



@app.route("/login")
def login():
    auth_url = f"https://anilist.co/api/v2/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
   
    return redirect(auth_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Authorization code not received."

    # Exchange the authorization code for an access token
    token_url = "https://anilist.co/api/v2/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "redirect_uri": os.getenv("REDIRECT_URI"),
        "code": code
    }
    response = requests.post(token_url, json=payload, headers=API_HEADERS)

    if response.status_code == 200:
        # Store the access token in the session
        token_data = response.json()
        session["access_token"] = token_data["access_token"]

        # Fetch user details
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        viewer_query = """
        query {
          Viewer {
            id
            name
            avatar {
              large
            }
          }
        }
        """
        viewer_response = requests.post("https://graphql.anilist.co", json={"query": viewer_query}, headers=headers)

        if viewer_response.status_code == 200:
            viewer_data = viewer_response.json()["data"]["Viewer"]
            user_id = viewer_data["id"]
            username = viewer_data["name"]
            avatar_url = viewer_data["avatar"]["large"]

            # Add the user to the database
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/anilist.db"))
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Insert or update the user in the Users table
            cursor.execute("""
            INSERT OR IGNORE INTO Users (user_id, username, avatar_url)
            VALUES (?, ?, ?)
            """, (user_id, username, avatar_url))

            conn.commit()
            conn.close()

            # Store the user ID in the session for future use
            session["user_id"] = user_id

            return redirect("/dashboard")  # Redirect to the dashboard

        else:
            return f"Failed to fetch user details: {viewer_response.status_code} - {viewer_response.text}"
    else:
        return f"Failed to get access token: {response.status_code} - {response.text}"

@app.route("/fetch_anime_list", methods=["POST"])
def fetch_anime_list():
    access_token = session.get("access_token")
    if not access_token:
        return jsonify({"error": "User not logged in"}), 401

    user_anime_list = fetch_user_anime_list(access_token)
    if user_anime_list:
        # Save to database
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/anilist.db"))

        conn = sqlite3.connect(db_path, timeout = 5)
        cursor = conn.cursor()

        for anime_list in user_anime_list:
            list_name = anime_list["name"]
            for entry in anime_list["entries"]:
                anime = entry["media"]
                # Insert anime into Anime table
                cursor.execute("""
                INSERT OR IGNORE INTO Anime (anime_id, title_romaji, title_english, genres, episodes, average_score)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    anime["id"],
                    anime["title"]["romaji"],
                    anime["title"]["english"],
                    ", ".join(anime["genres"]),
                    anime["episodes"],
                    anime["averageScore"]
                ))

                # Insert user interaction into UserAnime table
                cursor.execute("""
                INSERT INTO UserAnime (user_id, anime_id, rating, favourites, status)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, anime_id) DO UPDATE SET
                    rating = COALESCE(EXCLUDED.rating, rating),
                    favourites = EXCLUDED.favourites,
                    status = EXCLUDED.status,
                    last_updated = CURRENT_TIMESTAMP
                """, (
                    session.get("user_id", 0),  # Replace with actual user ID
                    anime["id"],                # Anime ID
                    entry.get("score"),         # User's rating
                    entry["media"]["isFavourite"],  # Favorited or not
                    entry.get("status", list_name)  # Watch status
                ))


        conn.commit()
        conn.close()

        return jsonify({"message": "User anime list saved successfully."})
    else:
        return jsonify({"error": "Failed to fetch user anime list"}), 500


@app.route("/dashboard")
def dashboard():
    # Render the HTML template
    return render_template("dashboard.html")

def recommender():
    conn = sqlite3.connect("data/anilist.db")
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    anime_query = """
    SELECT anime_id, title_romaji, genres, average_score, favourites, episodes, relations, cover_image_large
    FROM Anime
    WHERE average_score IS NOT NULL AND average_score > 0 AND favourites > 100;
    """
    anime_df = pd.read_sql_query(anime_query, conn)
    user_query = """
    SELECT anime_id, rating, favourites
    FROM UserAnime
    WHERE user_id = ? AND (rating IS NOT NULL OR favourites > 0);
    """
    user_df = pd.read_sql_query(user_query, conn, params=(user_id,))
    print("anime_df['anime_id'] dtype:", anime_df['anime_id'].dtype)
    print("user_df['anime_id'] dtype:", user_df['anime_id'].dtype)  
    print("anime_df columns:", anime_df.columns.tolist())
    print("user_df columns:", user_df.columns.tolist())
    print(f"user_id: {user_id}")
    print(user_df.head())

    # Split genres and one-hot encode
    anime_df['genres'] = anime_df['genres'].str.split(', ')
    anime_df['genres'] = anime_df['genres'].apply(
    lambda g_list: [g for g in g_list if g]  # remove empty strings
) 
    mlb = MultiLabelBinarizer()
    genre_vector = mlb.fit_transform(anime_df['genres'])
    genre_df = pd.DataFrame(genre_vector, columns=mlb.classes_, index=anime_df.index)
    anime_df = pd.concat([anime_df, genre_df], axis=1)

    # Normalize average_score and favourites
    scaler = MinMaxScaler()
    print(anime_df["average_score"])
    anime_df[['average_score', 'favourites']] = scaler.fit_transform(
        anime_df[['average_score', 'favourites']]
    )

    print("anime_df['anime_id'] dtype:", anime_df['anime_id'].dtype)
    print("user_df['anime_id'] dtype:", user_df['anime_id'].dtype)
    common_ids = set(anime_df['anime_id']).intersection(set(user_df['anime_id']))
    print("Number of overlapping anime_ids:", len(common_ids))
    print("Sample of overlapping anime_ids:", list(common_ids)[:10])
    # Merge with user data
    user_anime_df = user_df.merge(anime_df, on='anime_id', how='inner')
    print("Shape of user_anime_df:", user_anime_df.shape)
    print("Head of user_anime_df:", user_anime_df.head())
    print("user_anime_df columns:", user_anime_df.columns.tolist())
    print(user_anime_df["average_score"])
    print("Rows with NaN values in user_anime_df:")
    print("Mean of 'average_score':", user_anime_df['average_score'].mean())
    print("Mean of 'favourites_y':", user_anime_df['favourites_y'].mean())
    print(user_anime_df[user_anime_df.isnull().any(axis=1)])
    # Genre weighting
    user_genre_weights = user_anime_df[mlb.classes_].T.dot(user_anime_df['rating'])
    if user_genre_weights.sum() == 0:
        print("User genre weights sum to zero. Falling back to default weights.")
        user_genre_weights[:] = 1 / len(user_genre_weights)
    else:
        user_genre_weights /= user_genre_weights.sum()

    # Construct user vector
    # If you intend 'favourites' from the merged user side, check if it's _x or _y
    # For demonstration, let's assume 'favourites' from Anime is '_y'
    user_vector = pd.concat([
        user_genre_weights,
        pd.Series([
            user_anime_df['average_score'].mean(), 
            user_anime_df['favourites_y'].mean()  # if user_anime_df has favourites_y
        ], index=['average_score', 'favourites'])
    ])
    # Build anime vectors
    # Use the same columns in user_vector: mlb.classes_ + ['average_score', 'favourites']
    column_list = list(mlb.classes_) + ["average_score", "favourites"]
    print("Columns for final anime_vectors:", column_list)
    print("Check for NaNs in column_list individually:")
    print(anime_df[column_list].isnull().sum())  # Should all be 0
    print("Check for NaNs across rows in column_list:")
    print(anime_df[column_list].isnull().any(axis=1).sum())  # Rows with any NaN
    print("user_vector:", user_vector)
    print("NaNs in user_vector:", user_vector[user_vector.isnull()])
    print(len(user_vector))
    print("anime_df['anime_id'] dtype:", anime_df['anime_id'].dtype)
    print("user_df['anime_id'] dtype:", user_df['anime_id'].dtype)
    anime_vectors = anime_df[column_list].values
    print(len(anime_vectors))
    print("user_anime_df head:")
    print(user_anime_df.head())
    print("user_genre_weights:")
    print(user_genre_weights)
    print("Sum of user_genre_weights:", user_genre_weights.sum())
    
    # Compute similarity
    similarity_scores = cosine_similarity([user_vector], anime_vectors)[0]
    anime_df['similarity_score'] = similarity_scores

    # Exclude user’s already watched anime
    recommendations_df = anime_df[~anime_df['anime_id'].isin(user_df['anime_id'])]
    recommendations_df = recommendations_df[anime_df['episodes'] > 7]
    recommendations_df = recommendations_df[~recommendations_df['relations'].str.contains('"relationType": "PREQUEL"', na=False)]

    
    recommendations_df = recommendations_df.sort_values(by='similarity_score', ascending=False)
    recommendations_df.average_score *= 10
    top_n = 10
    print(recommendations_df[['anime_id', 'title_romaji']])
    return recommendations_df[['anime_id', 'title_romaji', 'similarity_score', 'genres', 'cover_image_large', 'average_score']].head(top_n)

@app.route("/run_recommender", methods=["POST"])
def run_recommender():
    recommendations = recommender()  # Assuming this returns a DataFrame
      # Check if recommendations are valid
    return jsonify({
            "message": "Recommender executed successfully!",
            "recommendations": recommendations.to_dict(orient="records")
        }), 200
if __name__ == "__main__":
    app.run(debug=True, port=8000)
