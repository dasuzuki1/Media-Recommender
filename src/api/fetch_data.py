import pip._vendor.requests as requests

API_URL = "https://graphql.anilist.co"
USER_AGENT = "Media-Recommender/1.0 (+https://github.com/dasuzuki1/Media-Recommender)"


def fetch_user_lists_by_username(username, media_type="ANIME"):
    """Fetch any AniList user's public list by username (no auth required).

    media_type: "ANIME" or "MANGA".
    Returns (viewer_dict, list_of_entries) where each entry has the shape
    {"score", "status", "media": {...}}. Empty list if the user is private
    or not found.
    """
    query = """
    query ($name: String, $type: MediaType) {
      MediaListCollection(userName: $name, type: $type) {
        user {
          id
          name
          avatar { large }
        }
        lists {
          name
          entries {
            score
            status
            media {
              id
              title { romaji english }
              description
              genres
              episodes
              averageScore
              favourites
              coverImage { large medium }
              isFavourite
            }
          }
        }
      }
    }
    """
    variables = {"name": username, "type": media_type}
    response = requests.post(
        API_URL,
        json={"query": query, "variables": variables},
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )

    if response.status_code != 200:
        print(f"AniList HTTP {response.status_code}: {response.text}")
        return None, []

    data = response.json()
    if "errors" in data:
        print(f"AniList GraphQL error: {data['errors']}")
        return None, []

    collection = data.get("data", {}).get("MediaListCollection")
    if not collection:
        return None, []

    viewer = collection.get("user")
    entries = []
    for lst in collection.get("lists", []):
        for entry in lst.get("entries", []):
            entries.append(entry)
    return viewer, entries


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


