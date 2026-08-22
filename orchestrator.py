import traceback
from dataclasses import dataclass
from agents import agent_1_downloader, agent_2_ocr, agent_3_date_parser, agent_4_validator, agent_5_supabase_writer
from config import settings

@dataclass
class PipelinePayload:
    pdfUrl: str
    equipmentId: str
    documentId: str
    companyId: str
    logId: str = None

async def run_pipeline(payload: PipelinePayload):
    """Runs all 5 agents in sequence. If any fails, logs error and stops."""
    
    print(f"🚀 Pipeline started for equipment {payload.equipmentId}")
    
    # Agent 1: Download PDF from Supabase Storage
    result = await agent_1_downloader.run(payload.pdfUrl)
    if not result.success:
        await _log_failure(payload, f"Agent 1 (Download): {result.error}")
        return {"success": False, "error": result.error}
    
    pdf_bytes = result.data
    print("✅ Agent 1: PDF downloaded")
    
    # Agent 2: Extract text using pdfplumber
    result = await agent_2_ocr.run(pdf_bytes)
    if not result.success:
        await _log_failure(payload, f"Agent 2 (OCR): {result.error}")
        return {"success": False, "error": result.error}
    
    extracted_text = result.data["text"]
    print(f"✅ Agent 2: Text extracted ({len(extracted_text)} chars)")
    
    # Agent 3: Parse date with GPT-4o (text only)
    result = await agent_3_date_parser.run(extracted_text)
    if not result.success:
        await _log_failure(payload, f"Agent 3 (LLM): {result.error}")
        return {"success": False, "error": result.error}
    
    parsed = result.data
    print(f"✅ Agent 3: Parsed date = {parsed.get('next_inspection_date')}")
    
    # Agent 4: Validate the parsed date
    result = await agent_4_validator.run(parsed)
    if not result.success:
        await _log_failure(payload, f"Agent 4 (Validator): {result.error}")
        return {"success": False, "error": result.error}
    
    validated = result.data
    print(f"✅ Agent 4: Validated date = {validated['next_inspection_date']}")
    
    # Agent 5: Write back to Supabase
    result = await agent_5_supabase_writer.run(
        validated, 
        payload.equipmentId, 
        payload.documentId, 
        payload.companyId,
        payload.logId
    )
    if not result.success:
        await _log_failure(payload, f"Agent 5 (Writer): {result.error}")
        return {"success": False, "error": result.error}
    
    print("✅ Agent 5: Saved to Supabase")
    print("🏁 Pipeline complete")
    
    return {
        "success": True, 
        "next_inspection_date": validated["next_inspection_date"]
    }

async def _log_failure(payload: PipelinePayload, error_msg: str):
    """Logs pipeline failure back to Supabase ai_actions_log."""
    import httpx
    
    SUPABASE_REST = f"{settings.SUPABASE_URL}/rest/v1"
    headers = {
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{SUPABASE_REST}/ai_actions_log?id=eq.{payload.logId}",
                headers=headers,
                json={
                    "status": "pending",
                    "description": f"Błąd pipeline: {error_msg} — wymaga weryfikacji ręcznej"
                }
            )
    except Exception as e:
        print(f"Failed to log failure: {e}")
