import json
import logging
from typing import List

from ..database.models import Anchor
from ..core.models import Detection
from .prompts import get_description_system_prompt, get_guidance_system_prompt
from .client import query_llm
from .utils import clean_llm_response

logger = logging.getLogger(__name__)

def format_anchors_for_llm(anchors: List[Anchor]) -> str:
    """
    Converts a list of Database Anchor objects into a clean JSON string 
    that the LLM can easily read to understand spatial context.
    """
    anchor_list = []
    for anchor in anchors:
        anchor_list.append({
            "name": anchor.name,
            "description": anchor.description,
            "location": {
                "x": round(anchor.x_center, 1),
                "y": round(anchor.y_center, 1)
            }
        })
    
    return json.dumps(anchor_list, indent=2)


def format_detections_for_llm(detections: List[Detection]) -> str:
    """
    Converts a list of current Detections (from YOLO) into a structured 
    JSON string. Includes the pre-calculated relative directions.
    """
    detection_list = []
    for det in detections:
        detection_list.append({
            "label": det.label,
            "confidence": round(det.confidence, 2),
            "position": {
                "relative_direction": det.relative_direction,
                "distance_estimate": det.distance_estimate
            }
        })
    
    return json.dumps(detection_list, indent=2)


def llm_generate_guidance(
    target_name: str,
    detections: List[Detection],
    anchors: List[Anchor]
) -> str:
    """
    The main coordinator for generating guidance.
    
    1. Formats visual and memory data.
    2. Constructs the System Prompt.
    3. Calls the LLM API.
    4. Cleans and returns the spoken instruction.
    """
    
    # 1. Format Inputs
    anchor_json = format_anchors_for_llm(anchors)
    detection_json = format_detections_for_llm(detections)
    
    # 2. Construct the Prompt
    system_prompt = get_guidance_system_prompt(
        target_name=target_name,
        anchor_json=anchor_json, 
        detection_json=detection_json
    )
    
    # 3. Call the LLM API
    user_query = f"Where is the {target_name}?"
    
    logger.info(f"Querying LLM for target: {target_name}")
    
    try:
        raw_response = query_llm(system_prompt, user_prompt=user_query)
    except Exception as e:
        logger.error(f"Failed to query LLM: {e}")
        return f"I'm sorry, I'm having trouble thinking right now. Please try again."

    # 4. Clean the Response
    guidance_text = clean_llm_response(raw_response)
    
    return guidance_text
