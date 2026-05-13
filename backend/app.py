from flask import Flask, request, jsonify
from flask_cors import CORS
from predictor import predict_engagement

app = Flask(__name__)
# Enable CORS for all routes (to allow React to communicate with Flask)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"}), 200

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
            
        # Get prediction results
        results = predict_engagement(title, description, tags)
        
        return jsonify(results), 200
        
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=5000)
