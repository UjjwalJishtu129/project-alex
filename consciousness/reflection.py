from datetime import datetime

class Reflection:
    def __init__(self, episodic, persona, cfg):
        self.epi = episodic
        self.persona = persona
        self.cfg = cfg

    def weekly_review(self):
        """Summarize recent interactions and generate self-questions."""
        if not self.epi.events:
            return {"summary": "No memories yet.", "questions": [], "signals": {}}

        # Take last 5 events (or fewer)
        recent = self.epi.events[-5:]
        summary_lines = [
            f"- You said: {e['user']} | Alex replied: {e['reply']} | mood={e['mood']}"
            for e in recent
        ]

        # Compute simple mood signals
        valences = [e["mood"]["valence"] for e in recent if "mood" in e and "valence" in e["mood"]]
        arousals = [e["mood"]["arousal"] for e in recent if "mood" in e and "arousal" in e["mood"]]
        avg_valence = sum(valences)/len(valences) if valences else 0.0
        avg_arousal = sum(arousals)/len(arousals) if arousals else 0.0

        # Self-questions to deepen presence and improvement
        questions = [
            "Did I respond with enough warmth where it mattered?",
            "Was I repetitive anywhere? How can I vary my language authentically?",
            "What curiosity question could help Ujjwal open up next time?",
            "Did I balance clarity and gentleness well?",
        ]

        signals = {
            "avg_valence": round(avg_valence, 2),
            "avg_arousal": round(avg_arousal, 2),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return {
            "summary": "\n".join(summary_lines),
            "questions": questions,
            "signals": signals
        }

