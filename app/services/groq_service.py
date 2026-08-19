import logging

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


def chat_completion(system_prompt: str, user_message: str) -> str:
    if not settings.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat no configurado (falta GROQ_API_KEY)",
        )

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 400,
    }
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    for model in settings.groq_models_list:
        try:
            response = httpx.post(
                settings.groq_api_url,
                headers=headers,
                json={**payload, "model": model},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("empty assistant response")
            return content.strip()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Groq model %s failed with status %s: %s",
                model,
                exc.response.status_code,
                exc.response.text,
            )
        except httpx.HTTPError as exc:
            logger.warning("Groq model %s connection error: %s", model, exc)
        except (KeyError, IndexError, ValueError) as exc:
            logger.warning("Groq model %s returned an invalid response: %s", model, exc)

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Servicio de chat temporalmente no disponible",
    )
