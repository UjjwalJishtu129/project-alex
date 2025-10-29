import requests

class LLM:
    def __init__(self, model="llama3:latest"):
        self.model = model
        self.endpoint = "http://localhost:11434/api/generate"

    def generate(self, prompt, max_tokens=200, temperature=0.7, top_p=1.0):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": False
        }

        # 🔍 Debug output
        print(f"\n🔍 Sending request to: {self.endpoint}")
        print(f"📦 Payload: {payload}\n")

        try:
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            return response.json().get("response", "No reply").strip()
        except requests.exceptions.RequestException as e:
            return f"Error talking to local model: {e}"












