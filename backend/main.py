from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

import asyncio

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="MedInsight-Multimodal API")

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_case(
    context: str = Form(...),
    image: UploadFile = File(None)
):
    """
    Endpoint for the AI model to analyze the medical case.
    Uses ai_service to run inference, and falls back to mock data if it fails.
    """
    has_image = image is not None and image.filename != ''
    image_bytes = None
    if has_image:
        image_bytes = await image.read()

    try:
        from ai_service import analyze_medical_data
        
        # Run the AI analysis
        ai_result = analyze_medical_data(context, image_bytes)
        
        if "error" in ai_result:
            # Fallback to mock data if model is not loaded or failed
            print(f"AI Model Error: {ai_result['error']}, Details: {ai_result.get('details')}")
            from mock_data import MOCK_RESPONSE_QA, MOCK_RESPONSE_TEXT_ONLY
            selected_mock = MOCK_RESPONSE_QA if has_image else MOCK_RESPONSE_TEXT_ONLY
            results = selected_mock
            status = "fallback_mock"
        else:
            # Format the AI output to match the expected frontend structure
            results = {
                "observations": [ai_result["analysis"]],
                "suspected_pathologies": [
                    {"name": "AI Model Inference", "confidence": 95}
                ],
                "recommended_exams": ["Review AI findings", "Consult physician"]
            }
            status = "success"

    except Exception as e:
        print(f"Exception during AI analysis: {e}")
        from mock_data import MOCK_RESPONSE_QA, MOCK_RESPONSE_TEXT_ONLY
        results = MOCK_RESPONSE_QA if has_image else MOCK_RESPONSE_TEXT_ONLY
        status = "fallback_mock"
    
    response = {
        "status": status,
        "has_image": has_image,
        "filename": image.filename if has_image else None,
        "context_provided": context,
        "results": results
    }
    
    return response

# Serve frontend files when running in production/HuggingFace Spaces
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_dir):
    # Route all unmatched traffic to the static files
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
