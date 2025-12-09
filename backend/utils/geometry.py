# backend/utils/geometry.py

from typing import Tuple

def calculate_relative_direction(x_center_norm: float, y_center_norm: float) -> str:
    """
    Converts normalized center coordinates (0.0 to 1.0) into a natural language direction.
    
    Args:
        x_center_norm: Normalized X-coordinate (0.0=left, 1.0=right).
        y_center_norm: Normalized Y-coordinate (0.0=top, 1.0=bottom).
        
    Returns:
        A string like "ahead and slightly to your left" or "directly down".
    """
    
    # X-Axis
    if x_center_norm < 0.35:
        x_dir = "to your **far left**"
    elif x_center_norm < 0.45:
        x_dir = "slightly to your **left**"
    elif x_center_norm > 0.65:
        x_dir = "to your **far right**"
    elif x_center_norm > 0.55:
        x_dir = "slightly to your **right**"
    else: 
        x_dir = "directly **ahead**"

    # Y-Axis
    if y_center_norm < 0.35:
        y_dir = "and **up**"
    elif y_center_norm > 0.65:
        y_dir = "and **down**"
    else:
        y_dir = "" 
        
    if x_dir == "directly **ahead**" and y_dir == "":
        return "directly **ahead**"
    
    return f"{x_dir}{y_dir}".strip().replace("ahead and", "ahead,")


def estimate_distance_simple(box_width_norm: float, box_height_norm: float) -> str:
    """
    Simple heuristic for distance based on object size in the frame.
    """
    area = box_width_norm * box_height_norm
    
    if area > 0.10: # Object takes up more than 10% of the frame area
        return "very close (less than half an arm's length)"
    elif area > 0.03:
        return "about an arm's length (approx. 0.5 - 1.0 meter)"
    elif area > 0.01:
        return "a few steps away (approx. 1.0 - 2.5 meters)"
    else:
        return "far away (more than 2.5 meters)"
