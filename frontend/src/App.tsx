import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Interfaces
interface DetectionBox {
  label: string;
  confidence: number;
  relative_direction: string;
  distance_estimate: string;
  box: { x_min: number; y_min: number; x_max: number; y_max: number };
}

interface ApiResponse {
  status: string;
  guidance_text: string;
  audio_path: string;
  target: string;
  annotated_image: string; 
  detections?: DetectionBox[];
}

// Components
function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  
  const [target, setTarget] = useState<string>("Initializing...");
  const [guidance, setGuidance] = useState<string>("Set a target to begin.");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [inputText, setInputText] = useState("");
  
  const [detections, setDetections] = useState<DetectionBox[]>([]);

  // Initialize Camera
  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 },
            audio: true 
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current?.play().then(() => setIsVideoReady(true));
          };
        }
      } catch (err) {
        console.error("Camera Error:", err);
        setGuidance("Error: Camera access denied.");
      }
    };
    startCamera();
  }, []);

  // draw loop
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    let animId: number;

    if (video && canvas && isVideoReady) {
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const render = () => {
        if (video.readyState >= 2) {
          if (canvas.width !== video.videoWidth) {
              canvas.width = video.videoWidth;
              canvas.height = video.videoHeight;
          }
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          // Overlay latest detections on top of live video
          detections.forEach((det) => {
            const { x_min, y_min, x_max, y_max } = det.box;
            ctx.strokeStyle = 'lime';
            ctx.lineWidth = 2;
            ctx.strokeRect(x_min, y_min, x_max - x_min, y_max - y_min);

            const label = `${det.label} ${(det.confidence * 100).toFixed(0)}%`;
            ctx.fillStyle = 'lime';
            ctx.font = '14px Arial';
            const textWidth = ctx.measureText(label).width;
            ctx.fillRect(x_min, y_min - 18, textWidth + 8, 18);

            ctx.fillStyle = 'black';
            ctx.fillText(label, x_min + 4, y_min - 4);
          });
        }
        animId = requestAnimationFrame(render);
      };
      render();
    }
    return () => { if (animId) cancelAnimationFrame(animId); };
  }, [isVideoReady, detections]);

  // Audio 
  const startRecording = () => {
    if (!videoRef.current?.srcObject) return;
    const stream = videoRef.current.srcObject as MediaStream;
    
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) audioChunksRef.current.push(event.data);
    };

    mediaRecorder.onstop = sendAudioCommand;
    mediaRecorder.start();
    setIsRecording(true);
    setGuidance("Listening...");
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudioCommand = async () => {
    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'command.wav');

    try {
      setGuidance("Processing voice...");
      const res = await axios.post('/api/set_target_from_audio', formData);
      if (res.data.target) {
        setTarget(res.data.target);
        setGuidance(`Target set to: ${res.data.target}`);
        setProcessedImage(null); 
      }
    } catch (err) {
      console.error("Audio Error:", err);
      setGuidance("Could not understand audio.");
    }
  };

  // Text
  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    try {
      await axios.post('/api/set_target_text', { name: inputText });
      setTarget(inputText);
      setGuidance(`Target set to: ${inputText}`);
      setInputText("");
      setProcessedImage(null); 
    } catch (err) {
      console.error("Text Error:", err);
    }
  };

  // Vision
  const captureAndProcess = async () => {
    if (!videoRef.current || !canvasRef.current || isProcessing) return;
    
    setIsProcessing(true);
    setGuidance("Analyzing...");
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (ctx && video.videoWidth > 0) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(async (blob) => {
        if (!blob) { setIsProcessing(false); return; }
        const formData = new FormData();
        formData.append('file', blob, 'capture.jpg');

        try {
          const res = await axios.post<ApiResponse>('/api/process_frame', formData);
          setGuidance(res.data.guidance_text);
          setTarget(res.data.target);
          setDetections(res.data.detections ?? []);
        } catch (error) {
          console.error("API Error", error);
          setGuidance("Error processing frame.");
        } finally {
          setIsProcessing(false);
        }
      }, 'image/jpeg');
    }
  };

  return (
    <div className="app-container">
      <h1>Vision Assistant</h1>
      
      <div className="status-bar">
        <p><strong>Current Target:</strong> {target}</p>
        <p className="guidance">{guidance}</p>
      </div>

      <div className="camera-view">
        <video ref={videoRef} autoPlay playsInline muted style={{ display: 'none' }} />
        <canvas ref={canvasRef} className="live-canvas" />
      </div>

      <div className="controls">
        {/* MANUAL INPUT */}
        <form onSubmit={handleManualSubmit} className="input-group">
          <input 
            type="text" 
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type object name..." 
          />
          <button type="submit">Set</button>
        </form>

        {/* BUTTONS */}
        <div className="button-group">
          <button 
            className={`mic-button ${isRecording ? 'recording' : ''}`}
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
          >
            {isRecording ? "Listening..." : "🎤 Speak"}
          </button>

          <button 
            className="scan-button"
            onClick={captureAndProcess} 
            disabled={isProcessing || !isVideoReady}
          >
            {isProcessing ? "Scanning..." : "🔍 Scan"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
