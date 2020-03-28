from typing import Dict

from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer

tokenizer = RegexTokenizer()

model = FastTextSocialNetworkModel(tokenizer=tokenizer)


class SentimentData:
    negative: float
    neutral: float
    skip: float
    speech: float
    positive: float

    def __init__(self, sentiment_data: Dict[str, float]):
        if 'negative' in sentiment_data:
            self.negative = sentiment_data['negative']
        if 'neutral' in sentiment_data:
            self.neutral = sentiment_data['neutral']
        if 'positive' in sentiment_data:
            self.positive = sentiment_data['positive']
        if 'speech' in sentiment_data:
            self.speech = sentiment_data['speech']
        if 'skip' in sentiment_data:
            self.skip = sentiment_data['skip']


def __get_sentiment(message: str) -> SentimentData:
    sentiment = model.predict([message])[0]
    return SentimentData(sentiment)


def get_toxicity(message: str) -> float:
    sentiment = __get_sentiment(message)
    if sentiment.negative > 0.7:
        return sentiment.negative
    else:
        return 0
