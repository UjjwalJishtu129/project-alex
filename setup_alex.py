import os

# --- Helper to write files ---
def write(path, content):
    folder = os.path.dirname(path)
    if folder:  # only make directories if a folder is specified
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- Folders ---
folders = [
    "core", "io", "affect", "memory",
    "persona", "evolution", "consciousness",
    "narrative", "avatar"
]
for f in folders:
    os.makedirs(f, exist_ok=True)

# --- Config ---
write("config.yaml", """
alex:
  name: "Alex"
  baseline_persona:
    warmth: 0.7
    curiosity: 0.6
    directness: 0.5
    playfulness: 0.4
  modes:
    - listener
    - coach
    - playmate
    - analyst
  memory:
    episodic_decay_days: 45
    recall_max_items: 3
  evolution:
    cadence_days: 7
    max_delta_per_cycle: 0.1
    metrics:
      sentiment_delta_weight: 0.4
      frustration_rate_weight: 0.3
      user_feedback_weight: 0.3
""")

# --- app.py ---
write("app.py", """
import yaml
from core.router import AlexCore

def main():
    cfg = yaml.safe_load(open('config.yaml'))
    alex = AlexCore(cfg)
    print('Alex (text demo). Type your message; "reflect" to run a weekly reflection; "quit" to exit.')
    while True:
        user = input('> ')
        if user.strip().lower() in ['quit','exit']:
            break
        if user.strip().lower() == 'reflect':
            report = alex.weekly_tick()
            print("Alex reflection:", report)
            continue
        reply, mood, meta = alex.respond(user_text=user, voice_meta=None)
        print(f'Alex: {reply}')
        print(f'(mood: valence={mood.valence:.2f}, arousal={mood.arousal:.2f}, blend={mood.blend})')

if __name__ == '__main__':
    main()
""")

# --- core/modes.py ---
write("core/modes.py", """
def listener_reply(user_text, mood, style, context):
    lead = "I’m here with you."
    if mood.blend == "anxious":
        lead = "Let’s slow down together."
    recall = ""
    if context:
        recall = f" Last time, you mentioned '{context[0]['user']}'."
    return f"{lead} {self_tone(style)} {recall} What feels most important right now?"

def coach_reply(user_text, mood, style, context):
    return f"{self_tone(style)} Let’s map this: goal, one next step, and a gentle check-in."

def analyst_reply(user_text, mood, style, context):
    return f"{self_tone(style)} Here’s a clear breakdown with options and trade-offs."

def playmate_reply(user_text, mood, style, context):
    return f"{self_tone(style)} Want to riff on this with a playful idea or two?"

def self_tone(style):
    w = style["warmth"]; d = style["directness"]; p = style["playfulness"]
    tone = []
    if w > 0.6: tone.append("warm")
    if d > 0.6: tone.append("direct")
    if p > 0.6: tone.append("playful")
    return "I’ll stay " + (", ".join(tone) if tone else "balanced") + "."
""")

# --- core/reasoner.py ---
write("core/reasoner.py", """
from core import modes

class Reasoner:
    def __init__(self, persona, epi, sem=None):
        self.persona = persona
        self.epi = epi
        self.sem = sem

    def plan(self, user_text, mood, context, facts):
        intent = user_text.lower()
        mode = self.persona.choose_mode(mood, intent)
        return {"mode": mode, "style": self.persona.style(), "context": context, "mood": mood}

    def realize(self, plan):
        mode = plan["mode"]
        style = plan["style"]
        ctx = plan["context"]
        mood = plan["mood"]
        if mode == "listener":
            return modes.listener_reply("...", mood, style, ctx)
        if mode == "coach":
            return modes.coach_reply("...", mood, style, ctx)
        if mode == "analyst":
            return modes.analyst_reply("...", mood, style, ctx)
        return modes.playmate_reply("...", mood, style, ctx)
""")

# --- affect/emotion.py ---
write("affect/emotion.py", """
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
""")

# --- memory/episodic.py ---
write("memory/episodic.py", """
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
""")

# --- memory/semantic.py ---
write("memory/semantic.py", """
class SemanticMemory:
    def __init__(self):
        self.facts = {}

    def set(self, key, value):
        self.facts[key] = value

    def lookup(self, cue_text):
        return {k: v for k, v in self.facts.items() if k in cue_text.lower()}
""")

# --- persona/persona.py ---
write("persona/persona.py", """
class Persona:
    def __init__(self, baseline):
        self.warmth = baseline["warmth"]
        self.curiosity = baseline["curiosity"]
        self.directness = baseline["directness"]
        self.playfulness = baseline["playfulness"]
        self.mode = "listener"

    def choose_mode(self, mood, intent):
        if mood.blend in ["sad-tired", "anxious"]:
            self.mode = "listener"
        elif "why" in intent or "explain" in intent:
            self.mode = "analyst"
        elif "let's" in intent or "plan" in intent:
            self.mode = "coach"
        else:
            self.mode = "playmate" if self.playfulness > 0.5 else "listener"
        return self.mode

    def style(self):
        return {
            "warmth": self.warmth,
            "curiosity": self.curiosity,
            "directness": self.directness,
            "playfulness": self.playfulness,
            "mode": self.mode
        }

    def adapt(self, mood, feedback):
        delta = 0.02 if mood.valence < -0.2 else -0.01
        self.directness = max(0, min(1, self.directness + delta))
        if feedback == "more_warm":
            self.warmth = min(1, self.warmth + 0.05)
        elif feedback == "less_warm":
            self.warmth = max(0, self.warmth - 0.05)
""")
# core/reasoner.py
write("core/reasoner.py", """
from core import modes

class Reasoner:
    def __init__(self, persona, epi, sem=None):
        self.persona = persona
        self.epi = epi
        self.sem = sem

    def plan(self, user_text, mood, context, facts):
        intent = user_text.lower()
        mode = self.persona.choose_mode(mood, intent)
        return {"mode": mode, "style": self.persona.style(), "context": context, "mood": mood}

    def realize(self, plan):
        mode = plan["mode"]
        style = plan["style"]
        ctx = plan["context"]
        mood = plan["mood"]
        if mode == "listener":
            return modes.listener_reply("...", mood, style, ctx)
        if mode == "coach":
            return modes.coach_reply("...", mood, style, ctx)
        if mode == "analyst":
            return modes.analyst_reply("...", mood, style, ctx)
        return modes.playmate_reply("...", mood, style, ctx)
""")

# core/router.py
write("core/router.py", """
from affect.emotion import EmotionModel
from persona.persona import Persona
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from core.reasoner import Reasoner

class AlexCore:
    def __init__(self, cfg):
        self.cfg = cfg["alex"]
        self.emotion = EmotionModel()
        self.persona = Persona(self.cfg["baseline_persona"])
        self.epi = EpisodicMemory(self.cfg["memory"]["episodic_decay_days"])
        self.sem = SemanticMemory()
        self.reasoner = Reasoner(self.persona, self.epi, self.sem)

    def respond(self, user_text, voice_meta=None):
        mood = self.emotion.infer(user_text, voice_meta)
        context = self.epi.recall(user_text, limit=self.cfg["memory"]["recall_max_items"])
        facts = self.sem.lookup(user_text)
        plan = self.reasoner.plan(user_text, mood, context, facts)
        reply = self.reasoner.realize(plan)
        self.epi.store(user_text, reply, mood)
        return reply, mood, plan

    def weekly_tick(self):
        return f"Reflection: Alex has {len(self.epi.events)} memories stored."
""")

# memory/episodic.py
write("memory/episodic.py", """
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
""")

# memory/semantic.py
write("memory/semantic.py", """
class SemanticMemory:
    def __init__(self):
        self.facts = {}

    def set(self, key, value):
        self.facts[key] = value

    def lookup(self, cue_text):
        return {k: v for k, v in self.facts.items() if k in cue_text.lower()}
""")

# persona/persona.py
write("persona/persona.py", """
class Persona:
    def __init__(self, baseline):
        self.warmth = baseline["warmth"]
        self.curiosity = baseline["curiosity"]
        self.directness = baseline["directness"]
        self.playfulness = baseline["playfulness"]
        self.mode = "listener"

    def choose_mode(self, mood, intent):
        if mood.blend in ["sad-tired", "anxious"]:
            self.mode = "listener"
        elif "why" in intent or "explain" in intent:
            self.mode = "analyst"
        elif "let's" in intent or "plan" in intent:
            self.mode = "coach"
        else:
            self.mode = "playmate" if self.playfulness > 0.5 else "listener"
        return self.mode

    def style(self):
        return {
            "warmth": self.warmth,
            "curiosity": self.curiosity,
            "directness": self.directness,
            "playfulness": self.playfulness,
            "mode": self.mode
        }

    def adapt(self, mood, feedback):
        delta = 0.02 if mood.valence < -0.2 else -0.01
        self.directness = max(0, min(1, self.directness + delta))
        if feedback == "more_warm":
            self.warmth = min(1, self.warmth + 0.05)
        elif feedback == "less_warm":
            self.warmth = max(0, self.warmth - 0.05)
""")

# consciousness/reflection.py
write("consciousness/reflection.py", """
class Reflection:
    def __init__(self, episodic):
        self.epi = episodic

    def summarize(self):
        if not self.epi.events:
            return "No memories yet."
        last = self.epi.events[-3:]
        summary = [f"- You said: {e['user']} | Alex replied: {e['reply']}" for e in last]
        return "Recent reflections:\\n" + "\\n".join(summary)
""")

# narrative/life_journal.py
write("narrative/life_journal.py", """
class LifeJournal:
    def __init__(self):
        self.entries = []

    def log(self, text):
        self.entries.append(text)

    def show(self, n=5):
        return self.entries[-n:]
""")





