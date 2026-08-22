import httpx
from dataclasses import dataclass

@dataclass
class AgentResult:
    success: bool
    data: any = None
    error: str = ""

async def run(pdf_url: str) -> AgentResult:
    """Downloads PDF from Supabase Storage. Returns raw bytes."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            
            if len(response.content) == 0:
                return AgentResult(success=False, error="Pusty plik PDF")
            
            if len(response.content) > 20 * 1024 * 1024:
                return AgentResult(success=False, error="Plik PDF za duży (max 20MB)")
            
            return AgentResult(success=True, data=response.content)
            
    except httpx.HTTPError as e:
        return AgentResult(success=False, error=f"Błąd pobierania PDF: {str(e)}")
