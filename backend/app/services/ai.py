import httpx

from app.core.config import get_settings


def _fallback_response(text: str) -> str:
    lowercase = text.lower()
    if "вод" in lowercase:
        return "Попробуй 5-минутный душ и проверь, нет ли протечек. Это дает стабильный эффект каждый день."
    if "транспорт" in lowercase or "машин" in lowercase:
        return "2-3 поездки в неделю на метро, автобусе или велосипеде уже заметно снижают личный след CO₂."
    if "мотивац" in lowercase or "сложно" in lowercase:
        return "Сфокусируйся на серии: одно небольшое действие в день лучше, чем идеальный, но редкий рывок."
    return "Отличный вопрос. Держи ритм: выбери 1 активити из воды, 1 из энергии и 1 из пластика сегодня."


def ai_response(text: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return _fallback_response(text)

    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты экологический ассистент EcoIZ. Отвечай кратко, дружелюбно и практично на русском языке.",
                    },
                    {"role": "user", "content": text},
                ],
                "temperature": 0.7,
                "max_tokens": 180,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"].strip()
        return content or _fallback_response(text)
    except Exception:
        return _fallback_response(text)
