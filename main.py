from fastapi import FastAPI
from pydantic import BaseModel
from orchestrator import run_pipeline, PipelinePayload

app = FastAPI(title="UDT AI Agent Pipeline")

class WebhookRequest(BaseModel):
    pdfUrl: str
    equipmentId: str
    documentId: str
    companyId: str
    logId: str = None

@app.post("/process-pdf")
async def process_pdf(request: WebhookRequest):
    """Receives webhook from Supabase Edge Function, runs pipeline."""
    payload = PipelinePayload(**request.dict())
    result = await run_pipeline(payload)
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}