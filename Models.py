class UserToxicityData:
    messages_count: int
    total_toxicity: float

    def __init__(self):
        self.messages_count: int = 0
        self.total_toxicity: float = 0

    def get_toxic_coefficient(self) -> float:
        return round(self.total_toxicity, 3)
