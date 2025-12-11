# Process

## Vision Layer - YOLOv8 and OpenCV
This layer handles the physical interpretation of the input image.

- *Image Loading (OpenCV)*: The raw JPEG file from the browser is decoded into a NumPy array (frame).
- *Object Detection (YOLOv8n)*: The frame is passed to the YOLOv8 Nano model for inference. It returns a list of Detections (bounding boxes, labels, confidence). 
- *Visualization (OpenCV)*: Before the image leaves the backend, the draw_detections_cv2 function uses OpenCV to render the green bounding boxes and labels directly onto the image pixels.

## AI & Guidance Layer - Gemini 2.5 Flash
This layer converts structured visual data into human-like guidance.

- *Prompt Generation*: The YOLO detection data is converted into a structured text prompt for the LLM.
- *Guidance Generation (Gemini)*: The Gemini 2.5 Flash model analyzes the prompt and generates an instruction (e.g., "The cup is to your left, near the keyboard.").

## Speech Layer - Whisper and gTTS
This layer handles the audio feedback pipeline.

- *Speech-to-Text (under development)*: Audio input is transcribed into a text prompt for the LLM.
- *Text-to-Speech (gTTS)*: The natural language guidance from the LLM is fed into the gTTS (Google Text-to-Speech) library, which generates an MP3 file.
- *Audio Serving*: The MP3 is saved to the public /data directory, and the resulting file path is included in the final JSON response.
