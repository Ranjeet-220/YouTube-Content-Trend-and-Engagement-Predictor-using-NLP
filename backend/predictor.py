import os
import joblib
import pandas as pd
from preprocess import preprocess_text, extract_features

# Global variables to cache models in memory
rf_model = None
tfidf_vectorizer = None

def load_models():
    global rf_model, tfidf_vectorizer
    if rf_model is None or tfidf_vectorizer is None:
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'rf_model.pkl')
        tfidf_path = os.path.join(os.path.dirname(__file__), 'model', 'tfidf.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(tfidf_path):
            raise FileNotFoundError("Model files not found. Please run train_model.py first.")
            
        rf_model = joblib.load(model_path)
        tfidf_vectorizer = joblib.load(tfidf_path)

def generate_suggestions(features):
    suggestions = []
    
    if features['title_word_count'] < 5:
        suggestions.append("Your title is quite short. Consider making it slightly longer (5-10 words) for better context.")
    if features['power_count'] == 0:
        suggestions.append("Add 'power words' to your title/description to capture attention (e.g., Ultimate, Proven, Best).")
    if features['curiosity_count'] == 0:
        suggestions.append("Try incorporating curiosity-inducing phrases (e.g., 'Secret', 'Find out') to increase click-through rate.")
    if features['sentiment_polarity'] < 0:
        suggestions.append("The overall sentiment is negative. Unless it's intentional (e.g., commentary), a positive tone generally performs better.")
    if features['title_exclamation_count'] == 0:
        suggestions.append("Consider using an exclamation mark in the title to convey excitement.")
    if features['seo_score'] < 70:
        suggestions.append("Your SEO score is low. Improve it by writing a more detailed description and adding more relevant tags.")
        
    if not suggestions:
        suggestions.append("Great job! Your title, description, and tags look optimized.")
        
    return suggestions

def determine_viral_probability(score):
    if score >= 80:
        return "Very High"
    elif score >= 60:
        return "High"
    elif score >= 40:
        return "Moderate"
    elif score >= 20:
        return "Low"
    else:
        return "Very Low"

def get_sentiment_label(polarity):
    if polarity > 0.3:
        return "Positive"
    elif polarity < -0.3:
        return "Negative"
    else:
        return "Neutral"

def predict_engagement(title, description, tags):
    load_models()
    
    # 1. Extract NLP features
    features = extract_features(title, description, tags)
    features_df = pd.DataFrame([features]).drop('seo_score', axis=1)
    
    # 2. Process text and extract TF-IDF features
    clean_txt = preprocess_text(f"{title} {description} {tags}")
    tfidf_matrix = tfidf_vectorizer.transform([clean_txt]).toarray()
    tfidf_df = pd.DataFrame(tfidf_matrix, columns=[f'tfidf_{i}' for i in range(tfidf_matrix.shape[1])])
    
    # 3. Combine features
    X_input = pd.concat([features_df, tfidf_df], axis=1)
    
    # 4. Predict
    prediction = rf_model.predict(X_input)[0]
    
    # Ensure score is within 0-100 bounds
    engagement_score = max(0, min(100, prediction))
    
    # 5. Build results
    results = {
        "engagement_score": round(engagement_score, 1),
        "viral_probability": determine_viral_probability(engagement_score),
        "seo_score": round(features['seo_score'], 1),
        "sentiment": get_sentiment_label(features['sentiment_polarity']),
        "improvement_suggestions": generate_suggestions(features)
    }
    
    return results
