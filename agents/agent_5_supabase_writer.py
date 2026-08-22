import httpx
from .agent_1_downloader import AgentResult
from config import settings

SUPABASE_REST = f"{settings.SUPABASE_URL}/rest/v1"

headers = {
    "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

async def run(validated_data: dict, equipment_id: str, document_id: str, company_id: str, log_id: str = None) -> AgentResult:
    """Writes extracted data back to Supabase."""
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Update equipment
            await client.patch(
                f"{SUPABASE_REST}/equipment?id=eq.{equipment_id}",
                headers=headers,
                json={
                    "next_inspection_date": validated_data["next_inspection_date"],
                    "status": "compliant"
                }
            )
            
            # 2. Update equipment_documents
            await client.patch(
                f"{SUPABASE_REST}/equipment_documents?id=eq.{document_id}",
                headers=headers,
                json={
                    "extracted_next_date": validated_data["next_inspection_date"]
                }
            )
            
            # 3. Update ai_actions_log
            if log_id:
                await client.patch(
                    f"{SUPABASE_REST}/ai_actions_log?id=eq.{log_id}",
                    headers=headers,
                    json={
                        "status": "done",
                        "description": f"Data następnej inspekcji wyodrębniona: {validated_data['next_inspection_date']}"
                    }
                )
            
            return AgentResult(success=True, data={"message": "Zapisano w Supabase"})
            
        except httpx.HTTPError as e:
            return AgentResult(success=False, error=f"Błąd zapisu do Supabase: {str(e)}")
