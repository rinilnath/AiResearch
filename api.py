"""
REST API with Auto-Generated Swagger Documentation
Run: uvicorn api:app --reload --port 8000
Access Swagger: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

from ai_agent import AIDefectAgent
from database import DefectDatabase

load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Manufacturing Defect AI Agent API",
    description="AI-powered defect management system with NLP, auto-categorization, and intelligent routing",
    version="1.0.0",
    contact={
        "name": "Manufacturing AI Team",
        "email": "team@manufacturing-ai.com"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize components
db = DefectDatabase()
api_key = os.getenv('ANTHROPIC_API_KEY')
agent = AIDefectAgent(api_key) if api_key else None


# Request/Response Models
class DefectReportRequest(BaseModel):
    description: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "description": "Hydraulic press on Line 3 leaking oil. Safety hazard on floor."
            }
        }
    }


class DefectReportResponse(BaseModel):
    ticket_id: str
    category: str
    priority: str
    assigned_team: str
    estimated_resolution_time: str
    recommended_actions: List[str]
    timestamp: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "ticket_id": "SAFE-20241024-001",
                "category": "Safety",
                "priority": "CRITICAL",
                "assigned_team": "Maintenance",
                "estimated_resolution_time": "2 hours",
                "recommended_actions": [
                    "Immediately secure area",
                    "Inspect hydraulic seals",
                    "Clean spill per safety protocol"
                ],
                "timestamp": "2024-10-24T10:30:00"
            }
        }
    }


class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = ""
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "RESOLVED",
                "notes": "Replaced hydraulic seal. Tested and verified."
            }
        }
    }


class DefectSummary(BaseModel):
    total_defects: int
    open_count: int
    critical_count: int
    high_count: int
    by_category: dict
    by_priority: dict


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API status"""
    return {
        "message": "Manufacturing Defect AI Agent API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.post("/api/v1/defects/report", response_model=DefectReportResponse, tags=["Defects"])
async def report_defect(request: DefectReportRequest):
    """
    **Report a new defect using natural language**
    
    - Uses AI/NLP to analyze defect description
    - Auto-categorizes defect type
    - Assigns priority level
    - Routes to appropriate team
    - Suggests solutions from historical data
    
    Returns structured defect ticket with AI analysis
    """
    if not agent:
        raise HTTPException(status_code=500, detail="AI Agent not initialized. Check API key.")
    
    try:
        # Get historical data for context
        historical_data = db.get_historical_defects()
        
        # Process with AI
        ai_result = agent.process_defect_report(
            request.description,
            historical_data if not historical_data.empty else None
        )
        
        # Create defect in database
        ticket_id = db.create_defect(ai_result)
        
        # Return response
        return DefectReportResponse(
            ticket_id=ticket_id,
            category=ai_result['category'],
            priority=ai_result['priority'],
            assigned_team=ai_result['assigned_team'],
            estimated_resolution_time=ai_result.get('estimated_resolution_time', 'Unknown'),
            recommended_actions=ai_result.get('recommended_actions', []),
            timestamp=ai_result['timestamp']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing defect: {str(e)}")


@app.get("/api/v1/defects", tags=["Defects"])
async def get_all_defects(status: Optional[str] = None, priority: Optional[str] = None):
    """
    **Get all defects with optional filters**
    
    - Filter by status: OPEN, IN_PROGRESS, RESOLVED
    - Filter by priority: CRITICAL, HIGH, MEDIUM, LOW
    
    Returns list of all defects
    """
    try:
        if status:
            defects = db.get_defects_by_status(status)
        elif priority:
            defects = db.get_defects_by_priority(priority)
        else:
            defects = db.get_all_defects()
        
        return {
            "count": len(defects),
            "defects": defects.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching defects: {str(e)}")


@app.get("/api/v1/defects/{ticket_id}", tags=["Defects"])
async def get_defect(ticket_id: str):
    """
    **Get specific defect by ticket ID**
    
    Returns complete defect details including:
    - Category and priority
    - Assigned team
    - Recommended actions
    - Status and resolution notes
    """
    try:
        defect = db.get_defect_by_ticket_id(ticket_id)
        
        if not defect:
            raise HTTPException(status_code=404, detail="Defect not found")
        
        return defect
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching defect: {str(e)}")


@app.put("/api/v1/defects/{ticket_id}/status", tags=["Defects"])
async def update_defect_status(ticket_id: str, request: StatusUpdateRequest):
    """
    **Update defect status**
    
    - Change status: OPEN → IN_PROGRESS → RESOLVED
    - Add resolution notes
    - Track status changes in history
    """
    try:
        success = db.update_defect_status(
            ticket_id,
            request.status,
            request.notes,
            "API User"
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Defect not found")
        
        return {
            "message": "Status updated successfully",
            "ticket_id": ticket_id,
            "new_status": request.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")


@app.get("/api/v1/analytics/summary", response_model=DefectSummary, tags=["Analytics"])
async def get_summary():
    """
    **Get analytics summary**
    
    Returns:
    - Total defects count
    - Open and critical defects
    - Distribution by category
    - Distribution by priority
    """
    try:
        stats = db.get_summary_stats()
        
        return DefectSummary(
            total_defects=stats['total_defects'],
            open_count=stats['open_count'],
            critical_count=stats['critical_count'],
            high_count=stats['high_count'],
            by_category=stats['by_category'],
            by_priority=stats['by_priority']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")


@app.get("/api/v1/teams", tags=["Teams"])
async def get_teams():
    """
    **Get all teams**
    
    Returns list of teams with contact information
    """
    try:
        teams = db.get_teams()
        return {
            "count": len(teams),
            "teams": teams.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teams: {str(e)}")


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "ai_agent": "ready" if agent else "not initialized"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
