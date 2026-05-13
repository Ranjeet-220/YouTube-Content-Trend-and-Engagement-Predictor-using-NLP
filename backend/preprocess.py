import re
import nltk
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Make sure the required NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    pass # In train_model.py we will explicitly download these

lemmatizer = WordNetLemmatizer()

# Predefined keyword lists
CURIOSITY_WORDS = ['secret', 'revealed', 'truth', 'mystery', 'hidden', 'discover', 'find out', 'what happens', 'you won\'t believe']
URGENCY_WORDS = ['now', 'fast', 'quick', 'hurry', 'limited time', 'today', 'instantly', 'urgent', 'before it\'s too late']
EMOTIONAL_WORDS = ['love', 'hate', 'amazing', 'terrible', 'shocking', 'insane', 'beautiful', 'sad', 'heartbreaking', 'hilarious']
POWER_WORDS = ['ultimate', 'complete', 'masterclass', 'guaranteed', 'proven', 'powerful', 'best', 'epic', 'massive', 'explosive']
CLICKBAIT_WORDS = ['gone wrong', 'omg', 'wtf', 'storytime', 'drama', 'exposed', 'cops called', 'prank', 'fail']
TRENDING_WORDS = ['2024', 'viral', 'trend', 'challenge', 'new', 'update', 'reacts', 'unboxing', 'review']

def preprocess_text(text):
    """Basic text cleaning: lowercase, alphanumeric+spaces, lemmatization, remove stopwords."""
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove special characters but keep alphanumeric and spaces for cleaning
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Tokenization & Lemmatization
    tokens = word_tokenize(clean_text)
    stop_words = set(stopwords.words('english'))
    
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(lemmatized_tokens)

def count_keywords(text, keyword_list):
    """Count occurrences of phrases/words from a list in the text."""
    text_lower = text.lower()
    count = 0
    for word in keyword_list:
        if word in text_lower:
            count += 1
    return count

def extract_features(title, description, tags):
    """Extract NLP features from the inputs."""
    combined_text = f"{title} {description} {tags}"
    blob = TextBlob(combined_text)
    
    # Sentiment & Subjectivity
    sentiment_polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Counts based on original raw title (where formatting matters)
    word_count = len(title.split())
    char_count = len(title)
    exclamation_count = title.count('!')
    number_count = sum(c.isdigit() for c in title)
    
    # Keyword matches
    curiosity_count = count_keywords(combined_text, CURIOSITY_WORDS)
    urgency_count = count_keywords(combined_text, URGENCY_WORDS)
    emotional_count = count_keywords(combined_text, EMOTIONAL_WORDS)
    power_count = count_keywords(combined_text, POWER_WORDS)
    clickbait_count = count_keywords(combined_text, CLICKBAIT_WORDS)
    trending_count = count_keywords(combined_text, TRENDING_WORDS)
    
    # Calculate an estimated SEO score purely on text features (out of 100)
    seo_score = 50 # Base score
    if len(title) > 40 and len(title) < 70: seo_score += 10
    if len(description) > 200: seo_score += 15
    if len(tags.split(',')) > 5: seo_score += 15
    if power_count > 0: seo_score += 10
    seo_score = min(100, seo_score)
    
    return {
        'sentiment_polarity': sentiment_polarity,
        'subjectivity': subjectivity,
        'title_word_count': word_count,
        'title_char_count': char_count,
        'title_exclamation_count': exclamation_count,
        'title_number_count': number_count,
        'curiosity_count': curiosity_count,
        'urgency_count': urgency_count,
        'emotional_count': emotional_count,
        'power_count': power_count,
        'clickbait_count': clickbait_count,
        'trending_count': trending_count,
        'seo_score': seo_score
    }
