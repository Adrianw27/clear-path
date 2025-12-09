import json
import logging
import cv2
import numpy as np
import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from .config import DATA_DIR
from .core.session import session_state
from .vision.detection import detect_objects
from .vision.visualization import draw_detections_cv2
from .audio.stt import transcribe_audio_to_text, extract_target_object
from .llm.models import llm_generate_guidance
from .llm.prompts import get_description_system_prompt
from .llm.client import query_llm 
from .llm.utils import clean_llm_response

app = FastAPI(title="Clear Path API")
logger = logging.getLogger(__name__)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

@app.on_event("startup")
def startup_event():
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    # initialize data base here later

# in memory storage for anchors for now
MOCK_ANCHORS = []

class MockAnchor:
    """Simple class to mimic the Database Anchor object"""
    def __init__(self, name, description, x, y):
        self.name = name
        self.description = description
        self.x_center = x
        self.y_center = y

# Helpers
def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

class TargetRequest(BaseModel):
    name: str

# Routes

@app.post("/api/set_target_text")
def set_target_text(request: TargetRequest):
    """Manually sets the target object from a text input."""
    session_state.set_target(request.name)
    return {"status": "success", "target": request.name}

@app.post("/api/set_target_from_audio")
def set_target_from_audio(audio_file: UploadFile = File(...)):
    """ Sets tagret from transcribed audio input. """
    temp_audio_path = Path(DATA_DIR) / "temp_user_input.wav"
    try:
        with open(temp_audio_path, "wb") as f:
            f.write(audio_file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio: {e}")

    command = transcribe_audio_to_text(str(temp_audio_path))
    if not command:
        raise HTTPException(status_code=400, detail="Could not transcribe audio.")
    
    target = extract_target_object(command)
    if target:
        session_state.set_target(target)
        return {"status": "success", "target": target}
    else:
        return {"status": "error", "message": "No target identified."}

@app.post("/api/process_frame")
def process_frame(file: UploadFile = File(...)):
    # db: Session = Depends(get_db)
    target_name = session_state.current_target_name or "person"

    # Load Image
    try:
        contents = file.file.read()
        frame = load_image_from_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")

    # Vision Inference
    try:
        detections = detect_objects(frame)
        session_state.update_detections(detections)
    except Exception as e:
        logger.error(f"Vision Error: {e}")
        raise HTTPException(status_code=500, detail="Vision processing failed.")

    # Draw boxes on backend
    annotated_frame = draw_detections_cv2(frame, detections)
    detection_payload = [
        {
            "label": d.label,
            "confidence": d.confidence,
            "relative_direction": d.relative_direction,
            "distance_estimate": d.distance_estimate,
            "box": {
                "x_min": d.box.x_min,
                "y_min": d.box.y_min,
                "x_max": d.box.x_max,
                "y_max": d.box.y_max,
            },
        }
        for d in detections
    ]
    
    # Encode to Base64 for frontend display
    success, buffer = cv2.imencode('.jpg', annotated_frame)
    if not success:
         raise HTTPException(status_code=500, detail="Could not encode image.")
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # LLM & TTS (do not let failures block detections)
    try:
        guidance_text = llm_generate_guidance(target_name, detections, MOCK_ANCHORS)
        # MVP: pause TTS and return text-only guidance
        audio_path = ""
    except Exception as e:
        logger.error(f"Guidance/TTS Error: {e}")
        guidance_text = "Vision processed, but guidance is temporarily unavailable."
        audio_path = ""

    return {
        "status": "guiding",
        "guidance_text": guidance_text,
        "audio_path": audio_path,
        "target": target_name,
        "annotated_image": f"data:image/jpeg;base64,{img_base64}",
        "detections": detection_payload,
    }

@app.post("/api/save_anchor")
def save_anchor(
    file: UploadFile = File(...),
    name: str = Body(..., description="Name of the anchor")
):
    # db: Session = Depends(get_db)

    try:
        contents = file.file.read()
        frame = load_image_from_bytes(contents)
        h, w, _ = frame.shape
        detections = detect_objects(frame)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision failed: {e}")

    if not detections:
        raise HTTPException(status_code=404, detail="No objects detected.")

    # Find best object (Largest)
    best_detection = max(
        detections, 
        key=lambda d: (d.box.x_max - d.box.x_min) * (d.box.y_max - d.box.y_min)
    )

    x_center = (best_detection.box.x_min + best_detection.box.x_max) / 2
    y_center = (best_detection.box.y_min + best_detection.box.y_max) / 2
    x_norm = x_center / w
    y_norm = y_center / h

    # LLM Description
    det_json = json.dumps([{"label": best_detection.label, "box_coords": (x_norm, y_norm)}])
    prompt = get_description_system_prompt(det_json, name)
    try:
        raw_desc = query_llm(prompt, user_prompt=f"Describe the {name}.")
        description = clean_llm_response(raw_desc)
    except:
        description = f"Auto-saved anchor for {name}"

    new_anchor = MockAnchor(name, description, x_norm * 100, y_norm * 100)
    MOCK_ANCHORS.append(new_anchor)
    print(f"Anchor Saved to Memory: {name}")

    return {"status": "Anchor saved", "anchor": {"name": name}}
