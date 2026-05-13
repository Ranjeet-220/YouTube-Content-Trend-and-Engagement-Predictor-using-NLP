from flask import Flask, request, jsonify
from flask_cors import CORS
from predictor import predict_engagement
import os
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

app = Flask(__name__)
CORS(app)

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    import re
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"}), 200

@app.route('/fetch-video', methods=['POST'])
def fetch_video():
    """Fetch YouTube video metadata using YouTube Data API v3."""
    try:
        data = request.get_json()
        url = data.get('url', '')

        if not url:
            return jsonify({"error": "YouTube URL is required"}), 400

        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL. Please provide a valid link."}), 400

        if not YOUTUBE_API_KEY:
            return jsonify({"error": "YouTube API key not configured on server."}), 500

        # Call YouTube Data API v3
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        yt_data = response.json()

        if not yt_data.get("items"):
            return jsonify({"error": "Video not found. It may be private or deleted."}), 404

        item = yt_data["items"][0]
        snippet = item["snippet"]
        stats = item.get("statistics", {})

        tags = snippet.get("tags", [])
        tags_str = ", ".join(tags) if tags else ""

        return jsonify({
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:1000],  # limit for UI
            "tags": tags_str,
            "views": stats.get("viewCount", "N/A"),
            "likes": stats.get("likeCount", "N/A"),
            "comments": stats.get("commentCount", "N/A"),
            "channel": snippet.get("channelTitle", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "published_at": snippet.get("publishedAt", "")
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to reach YouTube API: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        title = data.get('title', '')
        description = data.get('description', '')
        tags = data.get('tags', '')

        if not title:
            return jsonify({"error": "Title is required"}), 400

        results = predict_engagement(title, description, tags)
        return jsonify(results), 200

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
