from datetime import datetime, timedelta
from .agent_1_downloader import AgentResult

async def run(parsed_data: dict) -> AgentResult:
    """Validates that parsed date is reasonable for UDT inspection."""
    
    date_str = parsed_data.get("next_inspection_date")
    confidence = parsed_data.get("confidence", "low")
    
    if not date_str:
        return AgentResult(success=False, error="Brak daty w dokumencie")
    
    if confidence == "low":
        return AgentResult(success=False, error="Niska pewność modelu — wymaga weryfikacji człowieka")
    
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return AgentResult(success=False, error=f"Nieprawidłowy format daty: {date_str}")
    
    today = datetime.now().date()
    
    # Date must be in future
    if parsed_date <= today:
        return AgentResult(success=False, error=f"Data {date_str} jest w przeszłości")
    
    # UDT inspections are typically 3-24 months out
    max_future = today + timedelta(days=730)  # 2 years
    if parsed_date > max_future:
        return AgentResult(success=False, error=f"Data {date_str} jest za daleko w przyszłości (>{max_future})")
    
    return AgentResult(
        success=True, 
        data={
            "next_inspection_date": date_str,
            "decision_type": parsed_data.get("decision_type"),
            "equipment_code": parsed_data.get("equipment_code")
        }
    )
