#!/data/data/com.termux/files/usr/bin/bash
echo "🚀 Initializing C25 FaceForge..."

FACEFORGE_ROOT="$HOME/constellation25/faceforge"
mkdir -p "$FACEFORGE_ROOT"/{uploads,outputs,models}
cd "$FACEFORGE_ROOT"

# Create a virtual environment (recommended for Termux)
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install fastapi uvicorn python-multipart opencv-python numpy pillow

# Install InsightFace and ONNX Runtime
# (Note: If onnxruntime fails on Termux, use 'onnxruntime-qnn' or deploy to a cloud GPU)
pip install insightface onnxruntime

echo "✅ Dependencies installed. Downloading AI model..."

# Download the pre-trained InsightFace swap model (inswapper_128.onnx)
wget -O models/inswapper_128.onnx "https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx"

echo "✅ C25 FaceForge Setup Complete!"
