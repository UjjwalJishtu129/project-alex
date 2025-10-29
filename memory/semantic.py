class SemanticMemory:
    def __init__(self):
        self.facts = []

    def store_fact(self, text):
        """Store a simple fact string."""
        self.facts.append(text)

    def lookup(self, query):
        """Return all stored facts for now (can be made smarter later)."""
        return self.facts

