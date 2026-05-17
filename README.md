# Media Recommender

Personalized anime recommendations driven by your [AniList](https://anilist.co) watch history. Implemented in two iterations:

- **v1 — Flask MVP** (`src/`) — server-rendered Flask app with SQLite, on-demand recommender, AniList OAuth.
- **v2 — Serverless on AWS** (`aws/`) — same product, redesigned as Lambda + DynamoDB + EventBridge + API Gateway + CloudFront.


![Demo](https://github.com/user-attachments/assets/b16d7fc6-9d23-4bb1-8306-81bc440b510a)

## Stack

`Python` · `SQL` · `Flask` · `JavaScript` · `Terraform` · `AWS (Lambda, DynamoDB, API Gateway, EventBridge, SNS, S3, CloudFront)` · `scikit-learn` / `numpy`

## Architecture

### v2 (current)

```
Browser ──► CloudFront ──► S3 (static SPA)
   │
   └──► API Gateway ──► API Lambda ──► DynamoDB (Users, UserAnime, Recommendations)
                              │
                              └──► AniList GraphQL (OAuth + list sync)

EventBridge (hourly) ──► Compute Lambda ──► reads Anime + UserAnime
                                         └─► writes Recommendations
```

The compute Lambda runs a **hybrid recommender**:
- **Content-based** — genre one-hot vectors, cosine similarity to the user's rating-weighted preference vector.
- **Item-item collaborative** — co-occurrence among users who liked the same anime, normalized by item popularity.
- Final score: `content_weight * content + (1 - content_weight) * collaborative` (default 0.6 / 0.4).

The API Lambda only does a single DynamoDB `Query` per recommendation request — typical p50 latency under 100 ms.

### v1 (legacy, kept for reference)

Single Flask process, SQLite for both catalog and user data, recommender runs synchronously in the request handler. Lives in `src/`. Run with `python -m src.frontend.website`.
