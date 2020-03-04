class UserToxicityData:
    messages_count: int
    total_toxicity: float

    def __init__(self):
        self.messages_count: int = 0
        self.total_toxicity: float = 0

    def get_toxic_level(self) -> float:
        return round((self.total_toxicity / self.messages_count) * 100, 3)
