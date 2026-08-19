from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.report_schema import UserReportCreate, UserReportResponse
from backend.app.services.safety_service import ReportService

router = APIRouter(prefix="/reports", tags=["User Reports"])
report_service = ReportService()

@router.post("", response_model=UserReportResponse, status_code=status.HTTP_201_CREATED)
def submit_safety_report(report_data: UserReportCreate, db: Session = Depends(get_db)):
    if not (-90.0 <= report_data.latitude <= 90.0) or not (-180.0 <= report_data.longitude <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")

    created_report = report_service.create_user_report(db, report_data.dict())
    return {
        "id": created_report.id,
        "category": created_report.category,
        "severity": created_report.severity,
        "description": created_report.description,
        "latitude": created_report.latitude,
        "longitude": created_report.longitude,
        "status": created_report.status,
        "created_at": created_report.created_at.isoformat() if created_report.created_at else None
    }

@router.get("", response_model=List[UserReportResponse])
def list_user_reports(db: Session = Depends(get_db)):
    reports = report_service.get_user_reports(db)
    return [
        {
            "id": r["id"],
            "category": r["category"],
            "severity": r["severity"],
            "description": r["description"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "status": "ACTIVE",
            "created_at": r["created_at"]
        }
        for r in reports
    ]
