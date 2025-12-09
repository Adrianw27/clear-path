import logging
from pathlib import Path
import numpy as np
from typing import List
from ultralytics import YOLO
from ..core.models import Detection, BoundingBox
from ..utils.geometry import calculate_relative_direction, estimate_distance_simple

logger = logging.getLogger(__name__)
_model = None
MODEL_PATH = Path(__file__).resolve().parents[2] / "yolov8n.pt"

def get_model():
    global _model
    if _model is None:
        print("--> LOADING YOLO MODEL (This happens once)...")
        _model = YOLO(str(MODEL_PATH))
    return _model

def detect_objects(frame: np.ndarray) -> List[Detection]:
    print(f"--> RUNNING DETECTION on frame of shape: {frame.shape}")
    
    model = get_model()
    
    # Run Inference (Lowered conf to 0.25 to catch more objects)
    results = model.predict(frame, conf=0.25, verbose=False)
    result = results[0]
    
    structured_detections: List[Detection] = []
    frame_height, frame_width = frame.shape[:2]

    # Process Boxes
    for box in result.boxes:
        x_min, y_min, x_max, y_max = box.xyxy[0].cpu().numpy()
        confidence = float(box.conf[0].cpu().numpy())
        class_id = int(box.cls[0].cpu().numpy())
        label = model.names[class_id]

        print(f"    FOUND: {label} ({confidence:.2f})")

        # Geometry Logic
        box_width = x_max - x_min
        box_height = y_max - y_min
        x_center_norm = (x_min + (box_width / 2)) / frame_width
        y_center_norm = (y_min + (box_height / 2)) / frame_height
        
        det = Detection(
            label=label,
            box=BoundingBox(int(x_min), int(y_min), int(x_max), int(y_max)),
            confidence=confidence,
            relative_direction=calculate_relative_direction(x_center_norm, y_center_norm),
            distance_estimate=estimate_distance_simple(box_width / frame_width, box_height / frame_height)
        )
        structured_detections.append(det)

    if not structured_detections:
        print("    No objects detected.")

    return structured_detections
