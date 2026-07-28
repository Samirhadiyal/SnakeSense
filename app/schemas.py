# app/schemas.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class SpeciesPrediction(BaseModel):
    rank: int
    scientific_name: str
    common_name: str
    local_names: Dict[str, str]
    confidence_percentage: float
    toxicity_status: str
    venom_type: str
    is_big_four: bool

class PredictionResponse(BaseModel):
    status: str
    is_low_confidence: bool
    top_predictions: List[SpeciesPrediction]
    safety_disclaimer: str

class TriageRequest(BaseModel):
    bitten: bool
    time_elapsed_minutes: Optional[int] = 0
    local_swelling: bool = False
    drooping_eyelids: bool = False
    difficulty_breathing: bool = False
    spontaneous_bleeding: bool = False

class TriageResponse(BaseModel):
    urgency_level: str
    suspected_toxicity: str
    action_protocol: dict
    emergency_contacts: List[str]
    
class ChatRequest(BaseModel):
    query: str
    species_context: Optional[str] = ""
    language: Optional[str] = "English"

class ChatResponse(BaseModel):
    query: str
    answer: str
    language: str