# Clear Path AI Vision Assistant
An experimental vision and multimodal AI project designed to be a hands-free assistive tool providing visually impaired users with human-like directions for finding objects in their physical environment.

## Program Flow
Microphone audio capture -> **Whisper** speech to text processing (future implementation) -> webcam frame capture -> **OpenCV** image loading -> **YOLOv8** object detection ->  -> **Gemini 2.5 Flash** LLM guidance generation -> **gTTS** speech generation \n
- **Outputs:**
    - *OpenCV* processed image visualization with boundary boxes
    - *gTTS* audio for object location guidance

**Current Features:**
1. 👁️ *Computer Vision & Visualization*
- YOLOv8 Detection: The backend uses the YOLOv8 Nano model to detect 80+ common objects (cups, bottles, persons, cell phones, etc.) in real-time.
- Server-Side Drawing: Instead of relying on the browser, the backend uses OpenCV to draw green bounding boxes and labels directly onto the image before sending it back. This ensures what you see is exactly what the AI saw.
2. 🧠 *AI Guidance*
- Gemini 2.5 Flash Integration: The app uses Google's Gemini 2.5 Flash model to generate natural language instructions. It doesn't just say "cup"; it says "The cup is slightly to your right and close to you."
- Spatial Reasoning: The system calculates the relative position (left/right/center) and distance estimate of objects based on their bounding box size.
3. 💻 *Frontend Interface (React)*
- Live Camera Preview: Displays the live webcam feed so you can aim the camera.
- Text Input: The user can input a target name (e.g., "keyboard") to locate.

**Future Implementations:**
1. 🗣️ *Voice & Audio (Multimodal)*
- Text-to-Speech (TTS): The backend will generate an MP3 file of the guidance using gTTS and streams it to the browser, so the assistant speaks the results out loud.
- Push-to-Talk Voice Commands: The frontend will have a "Hold to Speak" button that records your voice, sends it to the backend, and sets the target object (e.g., "Find my keys") via audio transcription.
2. ⚓ *Set Anchors*
- Object Location: The user will be able to set anchors on objects in their physical environment. The AI model will will incorporate the anchors in the spatial reasoning to deliver a relative position to objects the user can easily locate.
- Database Integration: Environment anchors will be stored in a database and saved between sessions.

## Configuration/Setup

**Prerequisites**
* *Python 3.10+*
* *Node.js & npm*
* *Google Gemini API Key*

1. Setup Python virtual environment
```
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r backend/requirements.txt
```

2. Setup frontend
```
cd frontend
npm install
cd .. 
```
3. Configure API key (Free tier available at [Google AI Studio](https://aistudio.google.com/))
```
# Create .env file in backend/ to store API key
nvim backend/.env
# Paste GEMINI_API_KEY=your_api_key
:wq
```

## How to Run

Backend and frontend need to run simultaneously. You can use tmux to run multiple terminal sessions in one window.

1. Start backend
```
PYTHONPATH=. uvicorn backend.main:app --reload
```
5. Start frontend
```
cd frontend
npm run dev
# You should see - Local: http://localhost:5173
```

## How to Use

1. **Open Browser:** Go to http://localhost:5173.
2. **Permissions:** Click "Allow" when asked for Camera and Microphone access.
3. **Set a Target:**
    - *Text:* Type an object name (e.g., "cup", "bottle", "person") and press Set.
    - *Voice (future release):* Hold the "Hold to Speak" button, say "Find my cup", and release.
4. **Scan:** Point your camera at the object and click "Scan".
    - The app will freeze the frame, detect the object (Green Box), and relay its relative location.
