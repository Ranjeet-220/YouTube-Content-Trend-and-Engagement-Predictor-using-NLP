# YouTube Content Trend and Engagement Predictor using NLP

This is a fully functional AI-powered web application that predicts a YouTube video's engagement score based on its Title, Description, and Tags. It utilizes Natural Language Processing (NLP) to analyze sentiment, emotional intensity, and keywords, and employs a Random Forest Regression model to predict engagement.

## Features

- **Engagement Prediction**: Predicts an engagement score (0-100) using a Machine Learning model.
- **NLP Analysis**: Extracts sentiment, subjective tone, and powerful keywords using NLTK and TextBlob.
- **Viral Probability & SEO Score**: Provides actionable scores for video optimization.
- **Improvement Suggestions**: Recommends enhancements based on keyword density, sentiment, and length.
- **Futuristic UI**: A beautiful, modern, dark-mode React frontend built with Tailwind CSS and Chart.js.

## Project Structure

```
project/
├── backend/                  # Flask REST API and Machine Learning Pipeline
│   ├── app.py                # Flask application
│   ├── train_model.py        # Script to generate dataset and train the ML model
│   ├── predictor.py          # Prediction logic for live inputs
│   ├── preprocess.py         # NLP text processing
│   ├── model/                # Trained ML models
│   ├── dataset/              # Generated dummy datasets
│   └── requirements.txt      # Backend dependencies
├── frontend/                 # React frontend
│   ├── src/                  # React components and styling
│   └── package.json          # Frontend dependencies
└── README.md                 # Project documentation
```

## Setup Instructions

### 1. Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Train the model (this will generate `dummy_data.csv` and train the Random Forest model, as well as download NLTK data):
   ```bash
   python train_model.py
   ```
5. Start the Flask server:
   ```bash
   python app.py
   ```
   The server will run on `http://127.0.0.1:5000`.

### 2. Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The React app will typically be available at `http://localhost:5173`.

## API Usage

### `POST /predict`

**Request Body:**
```json
{
  "title": "HOW TO GO VIRAL ON YOUTUBE FAST!!!",
  "description": "In this video, I will show you the exact strategies to go viral on YouTube. Don't miss this amazing tutorial!",
  "tags": "youtube growth, viral, how to, tutorial"
}
```

**Response:**
```json
{
  "engagement_score": 87.5,
  "viral_probability": "High",
  "seo_score": 92.0,
  "sentiment": "Positive",
  "improvement_suggestions": [
    "Consider adding more power words to your title."
  ]
}
```

## Future Improvements

- Integrate real YouTube API data for live analysis.
- Use advanced deep learning models (e.g., BERT or Transformers) for text embeddings.
- Add A/B testing simulator for multiple thumbnail/title combinations.
