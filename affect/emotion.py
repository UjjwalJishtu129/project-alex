from dataclasses import dataclass

@dataclass
class Mood:
    valence: float
    arousal: float
    blend: str

class EmotionModel:
    def infer(self, text: str, voice_meta: dict | None) -> Mood:
        valence = self._text_valence(text)
        arousal = self._prosody_arousal(voice_meta) if voice_meta else self._text_arousal(text)
        blend = self._blend_label(valence, arousal, text)
        return Mood(valence=valence, arousal=arousal, blend=blend)

    def _text_valence(self, text):
        negatives = ["sad", "tired", "angry", "hurt", "alone", "fear"]
        positives = ["happy", "calm", "excited", "proud", "love", "hope"]
        score = sum(w in text.lower() for w in positives) - sum(w in text.lower() for w in negatives)
        return max(-1.0, min(1.0, score * 0.2))

    def _text_arousal(self, text):
        markers = ["!", "so", "very", "really"]
        score = sum(m in text for m in markers)
        return max(0.0, min(1.0, 0.2 + score * 0.15))

    def _prosody_arousal(self, meta):
        rate = meta.get("speech_rate", 1.0)
        pitch_var = meta.get("pitch_var", 0.5)
        return max(0.0, min(1.0, 0.3 * rate + 0.4 * pitch_var))

    def _blend_label(self, val, aro, text):
        t = text.lower()
        if val < -0.3 and aro > 0.6: return "anxious"
        if val < -0.2 and aro < 0.4: return "sad-tired"
        if val > 0.4 and aro > 0.6: return "excited"
        if "but" in t or "mixed" in t: return "bittersweet"
        return "calm-focused" if aro < 0.4 else "alert"
