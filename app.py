import yaml
from core.router import AlexCore

def main():
    cfg = yaml.safe_load(open('config.yaml'))
    alex = AlexCore(cfg)
    print('Alex (text demo). Type your message; "reflect" to run a weekly reflection; "quit" to exit.')
    print('You can also type "feedback: too_direct", "feedback: more_warm", or "feedback: more_clear".')

    while True:
        user = input('> ')
        if user.strip().lower() in ['quit','exit']:
            break

        # --- Step 3: Feedback hook ---
        if user.strip().lower().startswith("feedback:"):
            fb = user.split(":",1)[1].strip()
            alex.persona.adapt({"avg_valence":0,"avg_arousal":0}, alex.cfg["evolution"], feedback=fb)
            print(f"Alex: Thanks, I’ll adjust myself based on your feedback: {fb}")
            continue

        if user.strip().lower() == 'reflect':
            report = alex.weekly_tick()
            print("Alex reflection:\n" + report)
            continue

        reply, mood, meta = alex.respond(user_text=user, voice_meta=None)
        print(f'Alex: {reply}')
        print(f'(mood: valence={mood.valence:.2f}, arousal={mood.arousal:.2f}, blend={mood.blend})')

if __name__ == '__main__':
    main()


