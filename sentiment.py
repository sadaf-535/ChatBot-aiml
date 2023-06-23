from nltk.sentiment import SentimentIntensityAnalyzer
import random
from replies import negative_replies,positive_replies

def pick_random_string(strings):
    if not strings:
        return None
    random_string = random.choice(strings)
    return random_string

def get_max_sentiment_key(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    if sentiment_scores['compound'] >= 0.05:
        return pick_random_string(positive_replies)
    elif sentiment_scores['compound'] <= -0.05 or sentiment_scores['compound'] > -0.05:
        return pick_random_string(negative_replies)
    else:
        return pick_random_string(positive_replies)
    
print(get_max_sentiment_key("I just got promoted at work!"))