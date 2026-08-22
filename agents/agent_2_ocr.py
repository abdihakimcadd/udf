import pdfplumber
from dataclasses import dataclass
from .agent_1_downloader import AgentResult

@dataclass
class ExtractedContent:
    text: str

async def run(pdf_bytes: bytes) -> AgentResult:
    """Extracts text from PDF using pdfplumber. No compilation needed."""
    try:
        text_parts = []
        
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        combined_text = "\n".join(text_parts).strip()
        
        if len(combined_text) < 50:
            return AgentResult(
                success=False, 
                error="PDF zawiera za mało tekstu — prawdopodobnie skan obrazu. Wymaga ręcznej weryfikacji."
            )
        
        return AgentResult(success=True, data={"text": combined_text})
        
    except Exception as e:
        return AgentResult(success=False, error=f"Błąd OCR: {str(e)}")
