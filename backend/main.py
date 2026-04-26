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
        from backend.ai_service import analyze_medical_data
        
        # Run the AI analysis
        ai_result = analyze_medical_data(context, image_bytes)
        
        if "error" in ai_result:
            # Return the exact error so we can debug why the model failed
            error_msg = f"AI Error: {ai_result['error']} | {ai_result.get('details')}"
            results = {
                "observations": [error_msg],
                "suspected_pathologies": [{"name": "Error Loading AI", "confidence": 0}],
                "recommended_exams": ["Check backend logs"]
            }
            status = "error"
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
        error_msg = f"Critical Server Error: {str(e)}"
        print(error_msg)
        results = {
            "observations": [error_msg],
            "suspected_pathologies": [{"name": "Fatal Exception", "confidence": 0}],
            "recommended_exams": ["Check Kaggle Console"]
        }
        status = "error"
    
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
