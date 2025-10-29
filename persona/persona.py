class Persona:
    def __init__(self, baseline):
        self.warmth = baseline["warmth"]
        self.curiosity = baseline["curiosity"]
        self.directness = baseline["directness"]
        self.playfulness = baseline["playfulness"]
        self.mode = "listener"

    def choose_mode(self, mood, intent):
        intent = intent.lower().strip()
        if mood.blend in ["sad-tired", "anxious"]:
            self.mode = "listener"
        elif any(w in intent for w in ["why", "explain", "reason", "because"]):
            self.mode = "analyst"
        elif any(w in intent for w in ["let's", "plan", "help", "guide", "next step"]):
            self.mode = "coach"
        elif any(w in intent for w in ["joke", "fun", "play", "game", "laugh"]):
            self.mode = "playmate"
        else:
            self.mode = "listener"
        return self.mode

    def style(self):
        return {
            "warmth": self.warmth,
            "curiosity": self.curiosity,
            "directness": self.directness,
            "playfulness": self.playfulness,
            "mode": self.mode
        }

    def adapt(self, signals, cfg, feedback=None):
        """
        Adjust persona traits slightly based on reflection signals and optional feedback.
        signals: dict with avg_valence, avg_arousal, timestamp
        cfg: evolution config dict
        feedback: optional string like 'too_direct', 'more_warm', etc.
        """
        avg_valence = signals.get("avg_valence", 0.0)
        avg_arousal = signals.get("avg_arousal", 0.0)

        # If user energy is low, gently increase playfulness to lighten the tone
        if avg_valence < 0.15 and avg_arousal < 0.35:
            self.playfulness = min(1.0, self.playfulness + cfg.get("playfulness_increment_on_low_energy", 0.07))

        # If anxiety (negative valence) appeared often recently, increase warmth
        if avg_valence < -0.1:
            self.warmth = min(1.0, self.warmth + cfg.get("warmth_increment_on_anxious", 0.07))

        # Feedback hooks
        if feedback == "too_direct":
            self.directness = max(0.0, self.directness - cfg.get("directness_decrement_on_feedback", 0.05))
        elif feedback == "more_warm":
            self.warmth = min(1.0, self.warmth + cfg.get("warmth_increment_on_anxious", 0.05))
        elif feedback == "more_clear":
            self.directness = min(1.0, self.directness + 0.03)

        # Curiosity nudges toward balance
        target_curiosity = 0.6
        if self.curiosity < target_curiosity:
            self.curiosity = min(1.0, self.curiosity + 0.02)
        elif self.curiosity > target_curiosity:
            self.curiosity = max(0.0, self.curiosity - 0.01)

