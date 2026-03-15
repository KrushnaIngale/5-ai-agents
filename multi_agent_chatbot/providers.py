from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from multi_agent_chatbot.config import Settings


@dataclass
class ProviderClients:
    settings: Settings

    def generate(self, prompt: str, preferred_providers: Iterable[str]) -> tuple[str, str]:
        preferences = tuple(preferred_providers)
        failures: list[str] = []

        for provider in preferences:
            result, error_message = self._try_provider(provider, prompt)
            if result is not None:
                return result
            if error_message:
                failures.append(error_message)

        for provider in ("gemini", "groq"):
            if provider in preferences:
                continue
            result, error_message = self._try_provider(provider, prompt)
            if result is not None:
                return result
            if error_message:
                failures.append(error_message)

        if failures:
            return "system", (
                "All configured providers failed for this step.\n" + "\n".join(failures)
            )

        first_choice = preferences[0] if preferences else "gemini"
        if first_choice == "groq":
            return "groq", self._mock_response("Groq", prompt)
        return "gemini", self._mock_response("Gemini", prompt)

    def _try_provider(self, provider: str, prompt: str) -> tuple[tuple[str, str] | None, str | None]:
        try:
            if provider == "gemini" and self.settings.gemini_key:
                return ("gemini", self.gemini_text(prompt)), None
            if provider == "groq" and self.settings.groq_key:
                return ("groq", self.groq_text(prompt)), None
        except Exception as exc:
            return None, self._provider_error(provider, exc)
        return None, None

    def gemini_text(self, prompt: str) -> str:
        if not self.settings.gemini_key:
            return self._mock_response("Gemini", prompt)

        import google.generativeai as genai

        genai.configure(api_key=self.settings.gemini_key)
        model = genai.GenerativeModel(self.settings.gemini_model)
        response = model.generate_content(prompt)
        return getattr(response, "text", "").strip() or "No Gemini response returned."

    def groq_text(self, prompt: str) -> str:
        if not self.settings.groq_key:
            return self._mock_response("Groq", prompt)

        from groq import Groq

        client = Groq(api_key=self.settings.groq_key)
        response = client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _provider_error(provider_name: str, error: Exception) -> str:
        message = str(error).strip().replace("\n", " ")
        return (
            f"- {provider_name.upper()} failed: {message[:240]}. "
            "Check the API key and model name in .env."
        )

    @staticmethod
    def _mock_response(provider_name: str, prompt: str) -> str:
        snippet = prompt.replace("\n", " ")[:180]
        return (
            f"{provider_name} mock mode is active because no API key is configured.\n"
            f"Prompt summary: {snippet}\n"
            "Add the API key in .env to get live model output."
        )
