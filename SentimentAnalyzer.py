from typing import Dict

from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer

tokenizer = RegexTokenizer()

model = FastTextSocialNetworkModel(tokenizer=tokenizer)


class SentimentData:
    negative: float
    low_negative: float
    neutral: float
    skip: float
    speech: float
    positive: float

    def __init__(self, sentiment_data: Dict[str, float] = {'negative': 0,
                                                           'neutral': 0,
                                                           'positive': 0,
                                                           'speech': 0,
                                                           'skip': 0}):
        if 'negative' in sentiment_data:
            if sentiment_data['negative'] > 0.31:
                self.negative = sentiment_data['negative']
                self.low_negative = 0
            else:
                self.negative = 0
                self.low_negative = sentiment_data['negative']
        if 'neutral' in sentiment_data:
            self.neutral = sentiment_data['neutral']
        if 'positive' in sentiment_data:
            self.positive = sentiment_data['positive']
        if 'speech' in sentiment_data:
            self.speech = sentiment_data['speech']
        if 'skip' in sentiment_data:
            self.skip = sentiment_data['skip']

    def __add__(self, other):
        self.negative += other.negative
        self.low_negative += other.low_negative
        self.skip += other.skip
        self.speech += other.speech
        self.positive += other.positive
        self.neutral += other.neutral
        return self


def get_sentiment(message: str) -> SentimentData:
    sentiment = model.predict([message])[0]
    return SentimentData(sentiment)
