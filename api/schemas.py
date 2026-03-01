"""Request/response schemas for Structure Analysis API."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ImageSourceType(str, Enum):
    DRONE = "drone"
    GOOGLE_MAPS = "google_maps"
    INSPECTION = "inspection"  # generic (e.g. report photos)


class AnalyzeRequest(BaseModel):
    """Single image analysis request (multipart form: file or base64)."""
    source_type: Optional[ImageSourceType] = Field(
        default=ImageSourceType.INSPECTION,
        description="Image source: drone, google_maps, or inspection",
    )
    # Image sent via form file or body; see endpoint.


class AnalysisResult(BaseModel):
    """Per-image analysis result."""
    damage_description: str = Field(..., description="Short natural language description of structural damage/defects")
    source_type: Optional[str] = None
    labels: Optional[list[dict]] = Field(default_factory=list, description="Optional structured labels (class, confidence)")
    model_id: Optional[str] = Field(None, description="Model name/version used")


class AnalyzeResponse(BaseModel):
    """Response for POST /v1/analyze."""
    success: bool = True
    results: list[AnalysisResult] = Field(..., description="One result per image")
    model_id: Optional[str] = None
