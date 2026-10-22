import time


class BaseLLM:
    name = "base"

    def complete(self, role, system, user, max_tokens=4000, temperature=0.4):
        raise NotImplementedError


class AnthropicLLM(BaseLLM):
    name = "anthropic"

    def __init__(self, api_key, generate_model, judge_model, attempts=3):
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.generate_model = generate_model
        self.judge_model = judge_model
        self.attempts = attempts
        self.send_temperature = True

    def complete(self, role, system, user, max_tokens=4000, temperature=0.4):
        model = self.judge_model if role == "judge" else self.generate_model
        value = 0.0 if role == "judge" else temperature
        last_error = None
        for attempt in range(self.attempts):
            try:
                params = {
                    "model": model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                }
                if self.send_temperature:
                    params["temperature"] = value
                response = self.client.messages.create(**params)
                return "".join(b.text for b in response.content if getattr(b, "type", "") == "text")
            except Exception as error:
                last_error = error
                if self.send_temperature and "temperature" in str(error).lower():
                    self.send_temperature = False
                    continue
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Model call failed after {self.attempts} attempts: {last_error}")
