from typing import List
from enum import Enum
from pydantic import BaseModel, Field

# Input Schema
class ConversationInput(BaseModel):
    conversation: str
    frequency: int

# Output Schema
class ScamTactic(str, Enum):
    """Enumeration of possible conversational scam tactics."""
    WRONG_NUMBER_INTRO = "wrong_number_intro"
    PERSONAL_INFO_SEEKING = "personal_information_seeking"
    RAPPORT_BUILDING = "rapport_building"
    FLATTERY_OR_ROMANCE = "flattery_or_romance"
    FINANCIAL_SUPPORT = "financial_support"
    FINANCIAL_GAIN_OPPORTUNITY = "financial_gain_opportunity"
    SENSE_OF_URGENCY = "fee_pressure"
    CHANNEL_SHIFTING_PROPOSAL = "channel_shifting_proposal"

class VerdictLabel(str, Enum):
    """Enumeration for the final classification label."""
    SCAM = "SCAM"
    BENIGN = "BENIGN"

class ConversationalScamVerdict(BaseModel):
    """
    Represents the final verdict of a conversational scam analysis,
    including the label, confidence, and tactics used.
    """
    label: VerdictLabel = Field(
        ..., 
        description="Labels the conversation as 'SCAM' or 'BENIGN'"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score (0.0 to 1.0) for the label"
    )
    tactics: List[ScamTactic] = Field(
        default_factory=list, 
        description="A list of scam tactics identified in the conversation."
    )