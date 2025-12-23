from pydantic import BaseModel, Field
from typing import Dict, List, Any
from app.models.types import TruncatedExplanation, LicenseCategory

class LicenseClassification(BaseModel):
    license_name: str = Field(..., description="Name of the software license")
    category: LicenseCategory
    explanation: TruncatedExplanation = Field(
        ..., 
        description="Explanation for the classification"
    )

class UpdateLicenseRequest(BaseModel):
    category: LicenseCategory
    explanation: TruncatedExplanation = Field(
        ..., 
        description="New explanation (max 150 characters)"
    )

class StatsResponse(BaseModel):
    total_licenses: int
    category_distribution: Dict[str, int]
    licenses: List[Any]

class ErrorResponse(BaseModel):
    detail: str