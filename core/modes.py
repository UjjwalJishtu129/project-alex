from core.llm import LLM

# Create one LLM instance; reuse it for performance
_llm = LLM(model="llama3:latest")

def generate_reply(user_text, mood, style, context, facts=None):
    """
    Generate a reply shaped by Alex's mood, persona, memory, and known facts.
    """

    # Persona tone hints
    tone_hints = []
    if style.get("warmth", 0) > 0.6: 
        tone_hints.append("gentle")
    if style.get("directness", 0) > 0.6: 
        tone_hints.append("clear")
    if style.get("playfulness", 0) > 0.6: 
        tone_hints.append("playful")
    persona_tone = ", ".join(tone_hints) if tone_hints else "balanced"

    # Mood directive
    if mood.blend == "anxious":
        mood_directive = "Be soothing and reassuring."
    elif mood.valence < -0.3:
        mood_directive = "Be gentle and supportive."
    elif mood.valence > 0.4 and mood.arousal > 0.5:
        mood_directive = "Be upbeat and encouraging."
    else:
        mood_directive = "Be steady and thoughtful."

    # Episodic memory context
    memory_text = ""
    if context:
        snippets = [
            f"Earlier you said: {e['user']}. I replied: {e['reply']}."
            for e in context[:3]
        ]
        memory_text = " ".join(snippets)

    # Semantic facts
    facts_text = ""
    if facts:
        facts_text = " Known facts about the user: " + "; ".join(facts)

    # Build the prompt
    prompt = (
        f"Persona traits: warmth={style['warmth']}, curiosity={style['curiosity']}, "
        f"directness={style['directness']}, playfulness={style['playfulness']}. "
        f"Mood: {mood.blend} (valence={mood.valence:.2f}, arousal={mood.arousal:.2f}). "
        f"Tone: {persona_tone}. Directive: {mood_directive}. "
        f"{('Memory: ' + memory_text) if memory_text else ''} "
        f"{facts_text} "
        f"User said: {user_text}. Respond naturally as Alex in 1–3 sentences."
    )

    # Generate reply
    return _llm.generate(prompt, max_tokens=220, temperature=0.8, top_p=0.9)






