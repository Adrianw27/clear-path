
# fix implementation later 

import os
import uuid
from gtts import gTTS
from ..config import DATA_DIR

def convert_text_to_audio(text_to_speak: str) -> str:
    """
    Uses Google TTS to convert text to an MP3 file.
    """
    if not text_to_speak:
        return ""
    
    try:
        # Generate a unique filename 
        filename = f"speech_{uuid.uuid4().hex[:8]}.mp3"
        file_path = os.path.join(DATA_DIR, filename)
        
        tts = gTTS(text=text_to_speak, lang='en')
        tts.save(file_path)
        
        # Return the URL path that the frontend will use
        return f"/data/{filename}"

    except Exception as e:
        print(f"TTS Error: {e}")
        return ""
