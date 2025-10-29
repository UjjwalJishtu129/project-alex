class LifeJournal:
    def __init__(self):
        self.entries = []

    def log(self, text):
        self.entries.append(text)

    def show(self, n=5):
        return self.entries[-n:]
