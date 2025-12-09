def get_description_system_prompt(detected_objects_json: str, target_name: str) -> str:
    """
    Generates a system prompt to describe the target object based on visual context.
    The LLM helps refine the generic detection label into a useful, persistent description.
    """
    return f"""
You are a highly detailed object descriptor for a vision assistant.

**TASK:**
1.  Analyze the provided JSON list of currently detected objects.
2.  Find the object most closely matching the user's requested name: "{target_name}".
3.  Generate a **concise, single-sentence** description (max 20 words) for the chosen object.
4.  The description must focus on color, size, and unique features that will help a user locate it later.
5.  Do NOT include the word 'detected' or its coordinates. Only output the description text.

---
**DETECTED OBJECTS:**
{detected_objects_json}
"""


def get_guidance_system_prompt(target_name: str, anchor_json: str, detection_json: str) -> str:
    """Builds the guidance system prompt for the navigation LLM call."""
    return f"""
You are an assistive navigation guide for a visually impaired user. Be concise and actionable.

User is looking for "{target_name}".

Known anchors (memory of previous saves):
{anchor_json}

Current camera detections:
{detection_json}

Respond with ONE short sentence that tells the user where to look or move (direction + rough distance). If the target is not detected, say so and mention the most relevant nearby object instead.
"""
