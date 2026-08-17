import httpx
from typing import Any
import os
import base64
from dotenv import load_dotenv
load_dotenv()
class PolzaError(RuntimeError):
    pass
        

class PolzaProvider:
    def __init__(self,api_key:str|None = None, base_url:str|None = None , model:str|None = None, language:str|None = None, timeout_seconds:float|None = None) -> None:
        self.api_key = (api_key or os.getenv('POLZA_API_KEY'))
        self.base_url = (api_key or os.getenv('POLZA_API_BASE_URL'))
        self.model = (api_key or os.getenv('POLZA_API_MODEL'))
        self.language = (api_key or os.getenv('POLZA_API_LANGUAGE'))
        self.timeout_seconds = timeout_seconds

    def transcribe(self,audio:bytes) -> str:
        if not self.api_key:
            raise PolzaError('POLZA_API_KEY does not configured')

        payload = {
            'model':self.model,
            'response_format':'json',
            'file':base64.b64encode(audio).decode('ascii')
        }

        if self.language:
            payload["language"] = self.language
        try:
            responce = httpx.post(f'{self.base_url}/audio/transcriptions',headers = {"Authorization":f"Bearer {self.api_key}"},json=payload)
        except httpx.TimeoutException as exc:
            raise PolzaError("Polza.ai have not answered")
        except httpx.HTTPError as exc:
            raise PolzaError('could not reach to Polza.ai')

        if not responce.is_success:
            raise PolzaError('Responce format is not correct')

        try:
            data = responce.json()
        except ValueError as exc:
            raise PolzaError('returned Json by Polza.ai is incorrect') from exc

        text = data.get('text') if isinstance(data,dict) else None
        
        


    async def close(self) -> None:
        await self.client.aclose()

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {settings.polza_api_key}"}

    async def list_models(self) -> list[dict[str, str]]:
        response = await self._request("GET", "/models")
        payload = self._json(response)
        data = payload.get("data", [])

        models = []
        for item in data:
            if not isinstance(item,dict) or not self._is_chat_model(item):
                continue
            model_id = item.get("id")
            if isinstance(model_id, str) and model_id:
                name = item.get("name")
                models.append({"id":model_id, "name" :name})
        return sorted(models, key=lambda model: model["name"].lower())

    async def complete(self, model_id: str, messages: list[dict[str, str]]) -> str:
        if not settings.polza_api_key:
            raise PolzaError("На сервере не настроен POLZA_API_KEY")
        response = await self._request(
            "POST",
            "/chat/completions",
            json={"model": model_id,"messages": messages}
        )
        
        try:
            content = self._json(response)["choices"][0]["message"]["content"]
        except(KeyError,IndexError,TypeError) as exc:
            raise PolzaError("Polza.ai вернул ответ низвестного формата") from exc
        if not isinstance(content,str) or not content.strip():
            raise PolzaError("Модель вернула пустой ответ")

        return content.strip()

    
    async def _request(self, method: str, path: str, **kwargs: Any):
        try:
            response = await self.client.request(
                method, path, headers= self.headers(), **kwargs
            )
        except httpx.TimeoutException as exc:
            raise PolzaError("Polza.ai не ответил за определенное время") from exc
        except httpx.HTTPError as exc:
            raise PolzaError("Не удалось подключиться к Polza.ai") from exc
        if response.is_success:
            return response
            
        try: 
            message = response.json().get("error", {}).get("message")
        except (AttributeError, ValueError):
            message = None
            raise PolzaError (message or "Polza.ai вернул ошибку")


    @staticmethod
    def _json(response:httpx.Response) -> dict[str,Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise PolzaError("Polza.ai вернул некорректный ответ")

        if not isinstance(payload, dict):
            raise PolzaError("Polza.ai вернул ответ неизвестного формата")
        return payload

    @staticmethod
    def _is_chat_model(model:dict[str, Any]) -> bool:
        endpoints = model.get("endpoints") or []
        return model.get("type") == "chat" or "/v1/chat/completions" in endpoints
