import json
import httpx
from .agent_1_downloader import AgentResult
from config import settings

async def run(text: str) -> AgentResult:
    """Uses GPT-4o to extract next inspection date from UDT document text."""
    
    system_prompt = """Jesteś ekspertem od dokumentów UDT (Urząd Dozoru Technicznego) w Polsce.
    Twoim zadaniem jest wyodrębnienie daty następnej inspekcji/terminu kolejnego badania z decyzji UDT.
    
    Zwróć TYLKO obiekt JSON w formacie:
    {
        "next_inspection_date": "YYYY-MM-DD",
        "decision_type": "pozytywna" | "warunkowa" | "negatywna",
        "equipment_code": "string lub null",
        "confidence": "high" | "medium" | "low"
    }
    
    Jeśli nie możesz znaleźć daty, zwróć:
    {"next_inspection_date": null, "decision_type": null, "equipment_code": null, "confidence": "low"}
    
    Daty w dokumentach UDT są zazwyczaj w formacie DD.MM.YYYY lub YYYY-MM-DD."""
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Dokument UDT do analizy:\n\n{text}"}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }
            )
            response.raise_for_status()
            
            result = response.json()
            parsed = json.loads(result["choices"][0]["message"]["content"])
            
            return AgentResult(success=True, data=parsed)
            
    except Exception as e:
        return AgentResult(success=False, error=f"Błąd LLM: {str(e)}")
