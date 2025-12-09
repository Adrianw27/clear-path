from typing import Optional, List
from .models import Detection

class SessionManager:
    def __init__(self):
        self.current_target_name: Optional[str] = "person" 
        self.last_detections: List[Detection] = []
    
    def set_target(self, target_name: str):
        self.current_target_name = target_name
        print(f"Target set to: {target_name}")

    def clear_target(self):
        self.current_target_name = None

    def update_detections(self, detections: List[Detection]):
        self.last_detections = detections

session_state = SessionManager()
