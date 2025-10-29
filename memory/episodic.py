from datetime import datetime

class EpisodicMemory:
    def __init__(self, decay_days=45):
        self.decay_days = decay_days
        self.events = []

    def store(self, user_text, reply_text, mood):
        self.events.append({
            "ts": datetime.utcnow(),
            "user": user_text,
            "reply": reply_text,
            "mood": mood.__dict__
        })

    def recall(self, cue_text, limit=3):
        cue = cue_text.lower()
        scored = []
        for e in self.events:
            score = 0
            for token in cue.split():
                if token and token in e["user"].lower():
                    score += 1
            scored.append((score, e))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:limit]]
