import random
from affect.emotion import EmotionModel
from persona.persona import Persona
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from core.reasoner import Reasoner
from consciousness.reflection import Reflection

class AlexCore:
    def __init__(self, cfg):
        self.cfg = cfg["alex"]
        self.emotion = EmotionModel()
        self.persona = Persona(self.cfg["baseline_persona"])
        self.epi = EpisodicMemory(self.cfg["memory"]["episodic_decay_days"])
        self.sem = SemanticMemory()
        self.reasoner = Reasoner(self.persona, self.epi, self.sem)
        self.reflector = Reflection(self.epi, self.persona, self.cfg["evolution"])
        self.turns = 0  # count turns to auto-reflect

    def respond(self, user_text, voice_meta=None):
        mood = self.emotion.infer(user_text, voice_meta)
        context = self.epi.recall(user_text, limit=self.cfg["memory"]["recall_max_items"])
        facts = self.sem.lookup(user_text)

        # --- Step 4: crude fact learning ---
        if "i like" in user_text.lower():
            self.sem.store_fact(user_text.strip())
        elif "my name is" in user_text.lower():
            self.sem.store_fact(user_text.strip())

        plan = self.reasoner.plan(user_text, mood, context, facts)
        reply = self.reasoner.realize(plan)

        self.epi.store(user_text, reply, mood)
        self.turns += 1

        if self.turns % self.cfg["evolution"]["reflect_every_turns"] == 0:
            _ = self.weekly_tick()

        return reply, mood, plan


    def weekly_tick(self):
        """Run reflection and adapt persona slightly."""
        report = self.reflector.weekly_review()
        # Adapt persona using signals from reflection
        self.persona.adapt(report["signals"], self.cfg["evolution"])
        # Return a human-readable summary plus Alex's self-questions
        text = (
            "Reflection summary:\n" + report["summary"] +
            "\n\nQuestions I'm asking myself:\n" + ("\n".join(report["questions"]) if report["questions"] else "—") +
            f"\n\nSignals: valence={report['signals'].get('avg_valence', 0)}, arousal={report['signals'].get('avg_arousal', 0)}"
        )
        return text

