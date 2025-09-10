import numpy as np
import cv2  
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fer import FER

# Load facial expression model (fem)
def load_fem_model():
    return FER(mtcnn=True)

# Function to get facial expression metric (fem)
def get_fem(getFacialExp, detector, photo):
    if getFacialExp and photo is not None:
        file_bytes = np.asarray(bytearray(photo.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            gradient = 0.0
            return gradient
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = detector.detect_emotions(img_rgb)
        if not faces:
            gradient=0.0
            return gradient
        e = faces[0]['emotions']
        emotion_array=np.array([
            e['angry'],
            e['disgust'],
            e['fear'],
            e['happy'],
            e['sad'],
            e['surprise'],
            e['neutral']
        ])
        translation_array=np.array([
            -0.7,
            -0.4,
            -0.4,
            0.8,
            -0.9,
            0.4,
            0.0
            ])
        
        gradient=round(np.dot(emotion_array, translation_array),3)

        return (gradient, e)
    else:
        gradient=0.0
        return (gradient, None)

# Function to analyze sentiment and risk
def analyze_sentiment_and_risk(text, CRISIS_KEYWORDS):
    """
    Analyze sentiment and risk level from the input text.
    Returns sentiment score (-1 to 1), risk score (1 to 10), crisis level, and sentiment label.
    """
    # Placeholder implementation; replace with actual analysis logic
    # Simple TextBlob sentiment analysis (like your example)
    analyzer = SentimentIntensityAnalyzer()
    sentiment_dict =analyzer.polarity_scores(text)
    sentiment_score = sentiment_dict['compound']
    

    # Check for crisis keywords
    text_lower = text.lower()
    crisis_keywords_found = []
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            crisis_keywords_found.append(keyword)

    # Calculate risk score based on keywords and sentiment
    risk_score = 0

    # Crisis keywords are the primary indicator
    if crisis_keywords_found:
        risk_score += len(crisis_keywords_found) * 2  # Each keyword adds 2 points
    if sentiment_score > 0.2:
        sentiment_label = "Positive"
    elif sentiment_score < -0.2:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    # Determine crisis level
    if risk_score >= 8:
        crisis_level = "SEVERE"
    elif risk_score >= 6:
        crisis_level = "HIGH"
    elif risk_score >= 4:
        crisis_level = "MODERATE"
    else:
        crisis_level = "LOW"
    # Mental health indicators
        mental_health_words = ['depressed', 'depression', 'anxiety', 'anxious', 'panic', 'scared', 'suicidal', 'desperate', 'overwhelmed']
        mental_health_count = sum(1 for word in mental_health_words if word in text_lower)
        if mental_health_count > 0:
            risk_score += mental_health_count * 2
    # Normalize risk score to be between 1 and 10
    risk_score = min(max(risk_score, 1), 10)

    return sentiment_score, risk_score, crisis_level, sentiment_label