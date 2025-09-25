from pydantic import BaseModel, Field
from typing import List, Dict

class ChatMessage(BaseModel):
    """Represents a single message in the conversation history."""
    role: str
    text: str

class DebertaRequest(BaseModel):
    """Defines the input for the Deberta agent endpoint."""
    message: str = Field(..., description="The new message to process.")
    role: str = Field(..., description="The role of the sender (e.g., 'user' or 'agent').")
    history: List[ChatMessage] = Field([], description="The previous messages in the conversation.")

class DebertaResponse(BaseModel):
    """Defines the structured JSON response from the Deberta agent."""
    display_html: str
    scores: List[Dict]
    inference_time: float
    updated_history: List[ChatMessage]

class DebertaResetResponse(BaseModel):
    status: str
    message: str