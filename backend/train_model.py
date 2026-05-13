import os
import random
import pandas as pd
import numpy as np
import nltk
import joblib
import kagglehub
from kagglehub import KaggleDatasetAdapter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from preprocess import preprocess_text, extract_features

def download_nltk_data():
    print("Downloading NLTK Data...")
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

def load_kaggle_dataset(num_samples=5000):
    print("Downloading/Loading Kaggle dataset 'datasnaek/youtube-new'...")
    try:
        # Download the entire dataset which unzips it
        path = kagglehub.dataset_download("datasnaek/youtube-new")
        csv_path = os.path.join(path, "USvideos.csv")
        
        print(f"Loading CSV from {csv_path}...")
        df = pd.read_csv(
            csv_path,
            engine="python",
            on_bad_lines="skip",
            encoding_errors="ignore"
        )
    except Exception as e:
        print(f"Error loading Kaggle dataset: {e}")
        print("Fallback to generating dummy dataset...")
        # Fallback if download fails (e.g. checksum error)
        df = pd.DataFrame({
            "title": ["Fallback title " + str(i) for i in range(num_samples)],
            "description": ["Fallback description"] * num_samples,
            "tags": ["youtube, fallback"] * num_samples,
            "views": [random.randint(1000, 1000000) for _ in range(num_samples)],
            "likes": [random.randint(100, 50000) for _ in range(num_samples)],
            "comment_count": [random.randint(10, 5000) for _ in range(num_samples)]
        })

    # Drop rows where required text fields are missing
    df = df.dropna(subset=['title', 'description', 'tags'])
    
    # Map columns to what our model expects
    if 'comment_count' in df.columns:
        df['comments'] = df['comment_count']
        
    # Sample the dataset to speed up processing
    if len(df) > num_samples:
        print(f"Sampling {num_samples} rows from {len(df)} total rows...")
        df = df.sample(n=num_samples, random_state=42).reset_index(drop=True)
        
    # Cast necessary columns to numeric to avoid string multiplication errors
    df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
    df['comments'] = pd.to_numeric(df['comments'], errors='coerce').fillna(0)
    df['views'] = pd.to_numeric(df['views'], errors='coerce').fillna(0)

    # Simulate CTR between 2% and 15%
    df['ctr'] = np.random.uniform(2.0, 15.0, size=len(df))
    
    # Calculate Engagement Score
    # Formula: engagement_score = (likes * 0.4 + comments * 0.3 + ctr * 0.3)
    raw_score = (df['likes'] * 0.4) + (df['comments'] * 0.3) + (df['ctr'] * 0.3)
    
    # Normalize score between 0 and 100
    df['engagement_score'] = 100 * (raw_score - raw_score.min()) / (raw_score.max() - raw_score.min())
    
    # Save the processed dataset
    os.makedirs('dataset', exist_ok=True)
    df.to_csv('dataset/real_youtube_data.csv', index=False)
    print("Dataset saved to dataset/real_youtube_data.csv")
    
    return df

def train():
    download_nltk_data()
    
    dataset_path = 'dataset/real_youtube_data.csv'
    if not os.path.exists(dataset_path):
        df = load_kaggle_dataset(num_samples=5000)
    else:
        df = pd.read_csv(dataset_path)
        
    print("Extracting features (this may take a minute)...")
    
    # Textual features extraction
    nlp_features = []
    for idx, row in df.iterrows():
        if idx > 0 and idx % 1000 == 0:
            print(f"  Processed {idx} rows...")
        feats = extract_features(str(row['title']), str(row['description']), str(row['tags']))
        nlp_features.append(feats)
        
    features_df = pd.DataFrame(nlp_features)
    
    # Preprocess text for TF-IDF
    df['clean_text'] = df.apply(lambda row: preprocess_text(f"{row['title']} {row['description']} {row['tags']}"), axis=1)
    
    # TF-IDF Vectorization
    print("Vectorizing text...")
    tfidf = TfidfVectorizer(max_features=500)
    tfidf_matrix = tfidf.fit_transform(df['clean_text']).toarray()
    
    tfidf_df = pd.DataFrame(tfidf_matrix, columns=[f'tfidf_{i}' for i in range(tfidf_matrix.shape[1])])
    
    # Combine all features
    X = pd.concat([features_df.drop('seo_score', axis=1), tfidf_df], axis=1)
    y = df['engagement_score']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest model...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    score = rf_model.score(X_test, y_test)
    print(f"Model R^2 Score: {score:.4f}")
    
    os.makedirs('model', exist_ok=True)
    
    joblib.dump(rf_model, 'model/rf_model.pkl')
    joblib.dump(tfidf, 'model/tfidf.pkl')
    
    print("Models saved successfully in 'model/' directory.")

if __name__ == "__main__":
    train()
