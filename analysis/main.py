from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os
from typing import Optional

from services.analysis import AnalysisService
from services.llm_client import OllamaClient

app = FastAPI(title="PatternScope Analysis Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analysis_service = AnalysisService()
llm_client = OllamaClient(
    url=os.getenv('OLLAMA_URL', 'http://ollama:11434'),
    model=os.getenv('OLLAMA_MODEL', 'llama2')
)


class AnalysisRequest(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    methods: Optional[list[str]] = None


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "analysis"
    }


@app.post("/run-analysis")
async def run_analysis(request: AnalysisRequest):
    """Run anomaly detection analysis on traffic data"""
    try:
        # Validate date range
        start_dt = datetime.fromisoformat(request.start) if request.start else None
        end_dt = datetime.fromisoformat(request.end) if request.end else None

        # Run analysis
        result = await analysis_service.run_analysis(
            start=start_dt,
            end=end_dt,
            methods=request.methods or ['zscore', 'iqr', 'isolation_forest']
        )

        # Generate trend suggestions if anomalies were found
        if result['anomalies_detected'] > 0:
            suggestions = await llm_client.generate_trend_suggestions(
                anomalies=result['anomaly_details'],
                start=start_dt,
                end=end_dt
            )
            result['suggestions'] = suggestions

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv('PORT', '8000'))
    uvicorn.run(app, host="0.0.0.0", port=port)
