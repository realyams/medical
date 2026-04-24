from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

import asyncio

app = FastAPI(title="MedInsight-Multimodal API")

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to MedInsight Multimodal API. AI model integration pending."}

@app.post("/api/analyze")
async def analyze_case(
    context: str = Form(...),
    image: UploadFile = File(None)
):
    """
    Endpoint for the AI team to implement their model.
    Currently returns a mocked response for the frontend validation.
    """
    # Simulate processing time for the AI model
    await asyncio.sleep(2)
    
    # Check if an image was provided
    has_image = image is not None and image.filename != ''
    
    # In the future, the AI team will process the text (and optionally image) here.
    from mock_data import MOCK_RESPONSE_QA, MOCK_RESPONSE_TEXT_ONLY
    
    selected_mock = MOCK_RESPONSE_QA if has_image else MOCK_RESPONSE_TEXT_ONLY
    
    response = {
        "status": "success",
        "has_image": has_image,
        "filename": image.filename if has_image else None,
        "context_provided": context,
        "results": selected_mock
    }
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
