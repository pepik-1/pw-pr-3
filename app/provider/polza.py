import httpx

from typing import Any

import os
import base64

from dotenv import load_dotenv

load_dotenv()

class PolzaError(RuntimeError):
    pass
    

class PolzaProvider:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        language: str | None = None,
        timeout_seconds: float | None = None
    ) -> None:
        print("::", os.getenv("POLZA_API_KEY"))
        self.api_key  = (api_key or os.getenv("POLZA_API_KEY"))
        self.base_url = (base_url or os.getenv("POLZA_API_BASE_URL"))
        self.model    = (model or os.getenv("POLZA_MODEL"))
        self.language = (language or os.getenv("POLZA_LANGUAGE"))
        self.timeout_seconds = timeout_seconds
        
    def transcribe(self, audio: bytes) -> str:
        if not self.api_key:
            raise PolzaError("Не настроен POLZA_API_KEY")
        
        payload = {
            "model": self.model,
            "response_format": "json",
            "file": base64.b64encode(audio).decode("ascii")
        }
        
        if self.language:
            payload["language"] = self.language
            
        try:
            response = httpx.post(
                f"{self.base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=self.timeout_seconds
            )
        except httpx.TimeoutException as exc:
            raise PolzaError("Polza.ai не ответил за отведенное время.")
        except httpx.HTTPError as exc:
            raise PolzaError("Не удалось подключиться к Polza.ai")
        
        if not response.is_success:
            raise PolzaError("Ответ не в том формате")
        
        try:
            data = response.json()
        except ValueError as exc:
            raise PolzaError("Polza.ai вернул некорректный JSON") from exc
        
        text = data.get("text") if isinstance(data, dict) else None

        if not isinstance(text, str) or not text.strip():
            raise PolzaError("Polza.ai не вернул текст транскрибации")
        
        return text.strip()