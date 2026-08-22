import fitz  # PyMuPDF
import base64
from io import BytesIO
from dataclasses import dataclass
from .agent_1_downloader import AgentResult

@dataclass
class ExtractedContent:
    text: str
    images: list  # base64 encoded page images for vision fallback

async def run(pdf_bytes: bytes) -> AgentResult:
    """Extracts text from PDF. If text is too short, prepares images for vision."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        full_text = []
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract text
            text = page.get_text()
            full_text.append(text)
            
            # Render page to image (for vision fallback)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_bytes = pix.tobytes("png")
            images.append(base64.b64encode(img_bytes).decode("utf-8"))
        
        combined_text = "\n".join(full_text).strip()
        
        # If text is too short/garbled, signal that vision is needed
        if len(combined_text) < 50:
            return AgentResult(
                success=True, 
                data={"text": combined_text, "images": images, "needs_vision": True}
            )
        
        return AgentResult(
            success=True, 
            data={"text": combined_text, "images": images, "needs_vision": False}
        )
        
    except Exception as e:
        return AgentResult(success=False, error=f"Błąd OCR: {str(e)}")
