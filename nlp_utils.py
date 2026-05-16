from textblob import TextBlob
import re

def detect_mood(text):
    """
    Detects mood from text or emoji using TextBlob polarity and simple heuristics.
    Returns one of: 'Happy', 'Sad', 'Angry', 'Neutral', 'Excited', 'Relaxed'
    """
    if not text:
        return "Neutral"
        
    text_lower = text.lower()
    
    # Simple emoji/keyword matching first
    if any(word in text_lower for word in ['happy', 'joy', 'great', 'smile', '😊', '😁']):
        return "Happy"
    if any(word in text_lower for word in ['sad', 'cry', 'depressed', 'bad', '😢', '😭']):
        return "Sad"
    if any(word in text_lower for word in ['angry', 'mad', 'furious', '😡', '🤬']):
        return "Angry"
    if any(word in text_lower for word in ['excited', 'pumped', 'hype', '🤩', '🔥']):
        return "Excited"
    if any(word in text_lower for word in ['relax', 'chill', 'calm', 'tired', '😴', '😌']):
        return "Relaxed"
        
    # Fallback to TextBlob polarity
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.3:
        return "Happy"
    elif polarity < -0.3:
        return "Sad"
    else:
        return "Neutral"

def parse_chatbot_query(text):
    """
    Parses conversational chatbot text to extract:
    - Target Genres
    - Target Duration constraint (e.g., "under 90 mins")
    """
    genres = ["action", "comedy", "drama", "sci-fi", "romance", "horror", "thriller", "adventure", "animation"]
    text_lower = text.lower()
    
    found_genres = [g for g in genres if g in text_lower]
    
    # Try to extract duration
    max_duration = None
    # match patterns like "under 90 mins" or "less than 120"
    match = re.search(r'(under|less than|max)\s*(\d+)', text_lower)
    if match:
        max_duration = int(match.group(2))
        
    return {
        "genres": found_genres,
        "max_duration": max_duration
    }
