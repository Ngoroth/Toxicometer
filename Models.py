from collections import namedtuple
from datetime import datetime

from SentimentAnalyzer import SentimentData


class ToxicityData:
    messages_count: int
    total_sentiment_data: SentimentData
    changed_at: datetime

    def __init__(self):
        self.messages_count = 0
        self.total_sentiment_data = SentimentData()
        self.changed_at = datetime.now()

    def get_toxicity(self) -> float:
        toxicity = self.total_sentiment_data.high_negative - self.total_sentiment_data.positive / 5
        if toxicity > 0:
            return round(toxicity, 3)
        else:
            return 0

    def get_sentiment_data_coefficients(self) -> namedtuple('sentiment_percents',
                                                            ['negative', 'neutral', 'positive', 'other']):
        sentiment_percents = namedtuple('sentiment_percents', ['negative', 'neutral', 'positive', 'other'])
        negative = int(round(((self.total_sentiment_data.get_negative()) / self.messages_count) * 100))
        neutral = int(round((self.total_sentiment_data.neutral / self.messages_count) * 100))
        positive = int(round((self.total_sentiment_data.positive / self.messages_count) * 100))
        other = int(
            round(((self.total_sentiment_data.skip + self.total_sentiment_data.speech) / self.messages_count) * 100))
        return sentiment_percents(negative, neutral, positive, other)

    def get_main_sentiment(self) -> str:
        if self.total_sentiment_data.positive > self.total_sentiment_data.neutral \
                and self.total_sentiment_data.positive > self.total_sentiment_data.get_negative():
            return '😃'
        elif self.total_sentiment_data.get_negative() > self.total_sentiment_data.neutral \
                and self.total_sentiment_data.get_negative() > self.total_sentiment_data.positive:
            return '☹'
        else:
            return '😐'
