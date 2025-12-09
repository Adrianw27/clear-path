from dataclasses import dataclass
from typing import Optional

@dataclass
class BoundingBox:
    x_min: int
    y_min: int
    x_max: int
    y_max: int

@dataclass
class Detection:
    label: str
    box: BoundingBox
    confidence: float
    relative_direction: str = "" 
    distance_estimate: str = ""
