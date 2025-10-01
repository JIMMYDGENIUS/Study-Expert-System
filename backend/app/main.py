from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import GenerateRequest, GenerateResponse
from .scheduler import generate_schedule
from .exporters import ExportRegistry

import base64

app = FastAPI(title="Study Assistant", version="1.0.0")

# Allow frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # For development; restrict later to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registry for exporting schedules
export_registry = ExportRegistry()


@app.post("/api/generate", response_model=GenerateResponse)
def api_generate(req: GenerateRequest):
    """
    Generate a weekly study schedule based on user input.
    """
    try:
        result = generate_schedule(req)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Schedule generation failed: {exc}")

    # Store result for later export
    export_registry.store_last(result)
    return result


@app.get("/api/download/csv")
def api_download_csv():
    """
    Download the last generated schedule as CSV.
    """
    content, filename = export_registry.export_csv()
    if content is None:
        raise HTTPException(status_code=404, detail="No schedule available. Please generate one first.")

    return {
        "filename": filename,
        "content": content.decode("utf-8", errors="replace"),
        "mime": "text/csv",
    }


@app.get("/api/download/pdf")
def api_download_pdf():
    """
    Download the last generated schedule as PDF.
    """
    content, filename = export_registry.export_pdf()
    if content is None:
        raise HTTPException(status_code=404, detail="No schedule available. Please generate one first.")

    return {
        "filename": filename,
        "content_base64": base64.b64encode(content).decode("ascii"),
        "mime": "application/pdf",
    }
