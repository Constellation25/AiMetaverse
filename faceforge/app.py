# app.py — C25 FaceForge backend (InsightFace + ONNX Runtime)
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import os
import uuid
import shutil

app = FastAPI(title="C25 FaceForge API")

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize InsightFace models
print("🧠 Loading AI Models...")
app.state.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.state.app.prepare(ctx_id=0, det_size=(640, 640))

# Load the face swapper model
model_path = "models/inswapper_128.onnx"
if os.path.exists(model_path):
    app.state.swapper = insightface.model_zoo.get_model(model_path, providers=['CPUExecutionProvider'])
    print("✅ Models loaded successfully!")
else:
    print("⚠️ Model not found. Please download inswapper_128.onnx to the models/ folder.")
    app.state.swapper = None

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/api/swap")
async def swap_face(
    target_file: UploadFile = File(...),
    source_file: UploadFile = File(...)
):
    if not app.state.swapper:
        return {"error": "AI Model not loaded. Check server logs."}

    # Generate unique filenames
    target_id = str(uuid.uuid4()) + os.path.splitext(target_file.filename)[1]
    source_id = str(uuid.uuid4()) + os.path.splitext(source_file.filename)[1]
    output_id = "swapped_" + target_id

    target_path = os.path.join(UPLOAD_DIR, target_id)
    source_path = os.path.join(UPLOAD_DIR, source_id)
    output_path = os.path.join(OUTPUT_DIR, output_id)

    # Save uploaded files
    with open(target_path, "wb") as f:
        shutil.copyfileobj(target_file.file, f)
    with open(source_path, "wb") as f:
        shutil.copyfileobj(source_file.file, f)

    # Process Image/Video (Simplified for image first; video requires frame extraction)
    img_target = cv2.imread(target_path)
    img_source = cv2.imread(source_path)

    if img_target is None or img_source is None:
        return {"error": "Failed to read images. Ensure you uploaded valid image files."}

    # Detect faces
    faces_target = app.state.app.get(img_target)
    faces_source = app.state.app.get(img_source)

    if not faces_target or not faces_source:
        return {"error": "No face detected in one or both images."}

    # Swap face (using the first detected face in each)
    result_img = app.state.swapper.get(img_target, faces_target[0], faces_source[0], paste_back=True)

    # Save result
    cv2.imwrite(output_path, result_img)

    # Cleanup uploads to save space
    os.remove(target_path)
    os.remove(source_path)

    return {"success": True, "output_url": f"/outputs/{output_id}"}

@app.get("/outputs/{filename}")
async def get_output(filename: str):
    return FileResponse(os.path.join(OUTPUT_DIR, filename))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
