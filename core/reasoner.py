from core.modes import generate_reply

class Reasoner:
    def __init__(self, persona, epi, sem=None):
        self.persona = persona
        self.epi = epi
        self.sem = sem

    def plan(self, user_text, mood, context, facts):
        mode = self.persona.choose_mode(mood, user_text.lower().strip())
        return {
            "mode": mode,
            "style": self.persona.style(),
            "context": context,
            "mood": mood,
            "user_text": user_text,
            "facts": facts
        }


    def realize(self, plan):
        return generate_reply(
            user_text=plan["user_text"],
            mood=plan["mood"],
            style=plan["style"],
            context=plan["context"]
        )


