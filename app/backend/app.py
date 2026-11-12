
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
CORS(app)

NEWS_API = "https://hn.algolia.com/api/v1/search"

CATEGORIES = {
    "technology": "technology",
    "ai": "artificial intelligence",
    "business": "business",
    "science": "science",
    "programming": "programming",
    "startups": "startups",
    "general": "news"
}


def generate_summary(text):
    """Create a short extractive summary from available text."""
    if not text:
        return "Summary unavailable. Open the original article to read more."

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = " ".join(sentences[:2])

    if len(summary) > 400:
        summary = summary[:397] + "..."

    return summary


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "AI News Generator Backend is running!",
        "status": "success",
        "endpoints": [
            "/api/health",
            "/api/news",
            "/api/categories",
            "/api/summarize"
        ]
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI News Generator API"
    })


@app.route("/api/categories", methods=["GET"])
def categories():
    return jsonify({
        "status": "success",
        "categories": list(CATEGORIES.keys())
    })


@app.route("/api/news", methods=["GET"])
def get_news():
    category = request.args.get("category", "general").lower()
    limit = request.args.get("limit", 10, type=int)

    if category not in CATEGORIES:
        return jsonify({
            "status": "error",
            "message": "Invalid category",
            "available_categories": list(CATEGORIES.keys())
        }), 400

    if limit is None or limit < 1 or limit > 30:
        return jsonify({
            "status": "error",
            "message": "Limit must be between 1 and 30"
        }), 400

    try:
        response = requests.get(
            NEWS_API,
            params={
                "query": CATEGORIES[category],
                "tags": "story",
                "hitsPerPage": limit
            },
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        articles = []

        for item in data.get("hits", []):
            title = item.get("title") or item.get("story_title")
            url = item.get("url") or item.get("story_url")

            if not title or not url:
                continue

            story_text = item.get("story_text") or ""

            articles.append({
                "id": item.get("objectID"),
                "title": title,
                "description": generate_summary(story_text) if story_text else
                    "Read the original article for the full story.",
                "url": url,
                "author": item.get("author"),
                "points": item.get("points", 0),
                "category": category,
                "published_at": item.get("created_at")
            })

        return jsonify({
            "status": "success",
            "category": category,
            "total": len(articles),
            "articles": articles
        })

    except requests.RequestException:
        return jsonify({
            "status": "error",
            "message": "Unable to fetch news. Please try again later."
        }), 502


@app.route("/api/summarize", methods=["POST"])
def summarize():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not isinstance(text, str) or not text.strip():
        return jsonify({
            "status": "error",
            "message": "Please provide article text."
        }), 400

    if len(text) > 20000:
        return jsonify({
            "status": "error",
            "message": "Article text is too long. Maximum is 20000 characters."
        }), 400

    return jsonify({
        "status": "success",
        "summary": generate_summary(text)
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
