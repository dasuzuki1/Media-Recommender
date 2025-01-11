import pip._vendor.requests as requests

API_URL = "https://graphql.anilist.co"

def fetch_anime_with_favorites(min_favorites=50, page=1, per_page=50):
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        media(sort: FAVOURITES_DESC, type: ANIME) {
          id
          title {
            romaji
            english
          }
          description
          episodes
          averageScore
          favourites
          coverImage {
            large
            medium
          }
          relations{
                edges{
                    relationType
                node {
                        id
                    }
                }
                
                
                }
          genres
        }
      }
    }
    """
    variables = {"page": page, "perPage": per_page}
    response = requests.post(API_URL, json={"query": query, "variables": variables})

    # Check for HTTP errors
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)
        return []

    data = response.json()

    # Check for GraphQL errors
    if "errors" in data:
        print("GraphQL Error:", data["errors"])
        return []

    # Get all media and filter by min_favorites
    media_list = data.get("data", {}).get("Page", {}).get("media", [])
    filtered_list = [anime for anime in media_list if anime.get("favourites", 0) > min_favorites]
    return filtered_list


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
            favourites
            relation_type
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
                relations{
                edges{
                    relationType
                
                }
                
                
                }
            }
        }
    }
    """
    variables = {"page": page, "perPage": per_page}
    response = requests.post(API_URL, json={"query": query, "variables": variables})
    return response.json()["data"]["Page"]["media"]


