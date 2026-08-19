from typing import Optional
from pydantic import BaseModel, Field

class UserReportCreate(BaseModel):
    category: str = Field(..., example="Harassment")
    severity: int = Field(default=1, ge=1, le=5)
    description: Optional[str] = Field(default="", example="Unsafe corner near metro exit")
    latitude: float = Field(..., example=37.7749)
    longitude: float = Field(..., example=-122.4194)
    user_id: Optional[int] = None

class UserReportResponse(BaseModel):
    id: int
    category: str
    severity: int
    description: Optional[str]
    latitude: float
    longitude: float
    status: str
    created_at: Optional[str]

    class Config:
        from_attributes = True
