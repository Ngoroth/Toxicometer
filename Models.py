from collections import namedtuple

from SentimentAnalyzer import SentimentData


class UserToxicityData:
    messages_count: int
    total_sentiment_data: SentimentData

    def __init__(self):
        self.messages_count = 0
        self.total_sentiment_data = SentimentData()

    def get_toxicity(self) -> float:
        toxicity = self.total_sentiment_data.negative - self.total_sentiment_data.positive / 5
        if toxicity > 0:
            return round(toxicity, 3)
        else:
            return 0

    def get_sentiment_data_coefficients(self) -> namedtuple('sentiment_percents', ['negative', 'neutral', 'positive']):
        sentiment_percents = namedtuple('sentiment_percents', ['negative', 'neutral', 'positive'])
        negative = int(round((self.total_sentiment_data.negative / self.messages_count) * 100))
        neutral = int(round((self.total_sentiment_data.neutral / self.messages_count) * 100))
        positive = int(round((self.total_sentiment_data.positive / self.messages_count) * 100))
        return sentiment_percents(negative, neutral, positive)
