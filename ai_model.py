from textblob import TextBlob

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity

    if polarity <= -0.3:
        return "Sad 😔"
    elif polarity < 0:
        return "Low 😞"
    elif polarity < 0.3:
        return "Neutral 😐"
    else:
        return "Positive 😊"
