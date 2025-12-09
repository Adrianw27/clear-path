import cv2
import numpy as np
from .detection import Detection

def draw_detections_cv2(frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """
    Uses OpenCV to draw bounding boxes and labels directly onto the image array.
    """
    annotated_frame = frame.copy()

    for det in detections:
        x_min, y_min, x_max, y_max = det.box.x_min, det.box.y_min, det.box.x_max, det.box.y_max
        label = f"{det.label} {det.confidence:.2f}"
        
        cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated_frame, (x_min, y_min - text_h - 10), (x_min + text_w, y_min), (0, 255, 0), -1)

        cv2.putText(annotated_frame, label, (x_min, y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return annotated_frame
