import requests

API_URL = "https://graphql.anilist.co"

def fetch_anime_by_title(title):
    query = """
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            id
            title {
                romaji
                english
            }
            description
            episodes
            averageScore
            genres
        }
    }
    """
    variables = {"search": title}
    response = requests.post(API_URL, json={"query": query, "variables": variables})
    return response.json()

def fetch_popular_anime(page=1, per_page=10):
    query = """
    query ($page: Int, $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            media(sort: POPULARITY_DESC, type: ANIME) {
                id
                title {
                    romaji
                    english
                }
                description
                episodes
                averageScore
                genres
            }
        }
    }
    """
    variables = {"page": page, "perPage": per_page}
    response = requests.post(API_URL, json={"query": query, "variables": variables})
    return response.json()["data"]["Page"]["media"]
