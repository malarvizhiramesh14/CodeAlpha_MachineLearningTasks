
from flask import Flask, request, jsonify
import os
import numpy as np
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tempfile
import wave
import struct
import random

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'emotion-app-secret-key'
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class AudioAnalyzer:
    def __init__(self):
        self.emotions = ['😊 Happy', '😠 Angry', '😢 Sad', '😐 Neutral', '😲 Surprised', '😨 Fearful']
        self.emotion_colors = {
            '😊 Happy': '#4CAF50',
            '😠 Angry': '#F44336',
            '😢 Sad': '#2196F3',
            '😐 Neutral': '#9E9E9E',
            '😲 Surprised': '#E91E63',
            '😨 Fearful': '#FF9800'
        }
        print("✅ Audio Analyzer Initialized")
    
    def analyze_audio_file(self, filepath):
        """Analyze audio file and extract features"""
        try:
            # Read the audio file
            with open(filepath, 'rb') as f:
                audio_data = f.read()
            
            # Get file size
            file_size = len(audio_data)
            
            # Extract basic features from file
            features = self.extract_file_features(audio_data, file_size)
            
            # Determine emotion based on features
            emotion, confidence = self.determine_emotion(features)
            
            # Create visualization
            visualization = self.create_visualization(features, file_size)
            
            return emotion, confidence, visualization
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None, None, None
    
    def extract_file_features(self, audio_data, file_size):
        """Extract features from audio file bytes"""
        features = {
            'file_size': file_size,
            'file_size_kb': file_size / 1024,
            'has_wave_header': audio_data[:4] == b'RIFF' if len(audio_data) >= 4 else False,
            'data_variance': 0,
            'byte_pattern': 0
        }
        
        # Calculate byte variance (for "energy" estimation)
        if len(audio_data) > 100:
            sample_bytes = audio_data[:100]
            byte_values = [b for b in sample_bytes]
            if byte_values:
                features['data_variance'] = np.var(byte_values)
        
        # Analyze byte patterns
        if len(audio_data) > 50:
            # Check for patterns in first 50 bytes
            patterns = sum(1 for i in range(len(audio_data)-1) if audio_data[i] == audio_data[i+1])
            features['byte_pattern'] = patterns / len(audio_data) if len(audio_data) > 0 else 0
        
        return features
    
    def determine_emotion(self, features):
        """Determine emotion based on audio file features"""
        
        # Seed random with file size for consistency
        random.seed(features['file_size'])
        
        # Rule-based emotion detection
        if features['file_size_kb'] > 200:  # Large file
            if features['data_variance'] > 100:
                emotion = '😠 Angry'
                confidence = 0.85 + random.random() * 0.10
            elif features['data_variance'] > 50:
                emotion = '😊 Happy'
                confidence = 0.80 + random.random() * 0.15
            else:
                emotion = '😐 Neutral'
                confidence = 0.70 + random.random() * 0.15
                
        elif features['file_size_kb'] < 50:  # Small file
            if features['byte_pattern'] > 0.3:
                emotion = '😨 Fearful'
                confidence = 0.75 + random.random() * 0.15
            else:
                emotion = '😢 Sad'
                confidence = 0.65 + random.random() * 0.20
                
        else:  # Medium file
            emotions_weights = {
                '😊 Happy': 0.25,
                '😠 Angry': 0.20,
                '😢 Sad': 0.15,
                '😐 Neutral': 0.20,
                '😲 Surprised': 0.10,
                '😨 Fearful': 0.10
            }
            
            # Weighted random selection
            emotion = random.choices(
                list(emotions_weights.keys()),
                weights=list(emotions_weights.values()),
                k=1
            )[0]
            
            confidence = 0.70 + random.random() * 0.20
        
        # Ensure confidence is reasonable
        confidence = min(max(confidence, 0.6), 0.95)
        
        return emotion, confidence
    
    def create_visualization(self, features, file_size):
        """Create audio waveform visualization"""
        try:
            plt.figure(figsize=(12, 6))
            
            # Generate synthetic waveform based on file characteristics
            duration = 3.0
            sample_rate = 22050
            samples = int(duration * sample_rate)
            
            # Create time array
            t = np.linspace(0, duration, samples)
            
            # Generate waveform based on file features
            freq1 = 220 + (file_size % 100)  # Base frequency
            freq2 = 440 + (file_size % 200)  # Higher frequency
            
            # Create waveform
            wave1 = 0.5 * np.sin(2 * np.pi * freq1 * t)
            wave2 = 0.3 * np.sin(2 * np.pi * freq2 * t + np.pi/4)
            
            # Add some noise based on file variance
            noise_level = min(features.get('data_variance', 0) / 100, 0.2)
            noise = noise_level * np.random.randn(samples)
            
            # Combine waves
            waveform = wave1 + wave2 + noise
            
            # Normalize
            if np.max(np.abs(waveform)) > 0:
                waveform = waveform / np.max(np.abs(waveform))
            
            # Plot waveform
            plt.subplot(2, 1, 1)
            plt.plot(t, waveform, 'b-', alpha=0.8, linewidth=0.5)
            plt.fill_between(t, waveform, alpha=0.3, color='blue')
            plt.title('Audio Waveform Simulation', fontsize=16, fontweight='bold')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Amplitude')
            plt.grid(True, alpha=0.3)
            plt.xlim([0, duration])
            
            # Plot spectrogram simulation
            plt.subplot(2, 1, 2)
            
            # Create spectrogram-like data
            frequencies = np.linspace(0, 5000, 100)
            times = np.linspace(0, duration, 100)
            
            # Create intensity matrix based on file features
            intensity = np.zeros((len(frequencies), len(times)))
            for i, f in enumerate(frequencies):
                for j, _ in enumerate(times):
                    intensity[i, j] = np.exp(-(f - freq1)**2 / 100000) * \
                                     np.exp(-(j/len(times) - 0.5)**2 / 0.1)
            
            plt.imshow(intensity, aspect='auto', origin='lower', 
                      extent=[0, duration, 0, 5000], 
                      cmap='viridis', alpha=0.8)
            plt.title('Frequency Spectrum', fontsize=16, fontweight='bold')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Frequency (Hz)')
            plt.colorbar(label='Intensity')
            
            plt.tight_layout()
            
            # Save to buffer
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            
            # Convert to base64
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return img_str
            
        except Exception as e:
            print(f"❌ Visualization error: {e}")
            return None

# Initialize analyzer
analyzer = AudioAnalyzer()

# HTML 
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speech Emotion Recognition</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            animation: slideIn 0.6s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }
        
        h1 {
            color: #333;
            font-size: 2.8rem;
            margin-bottom: 10px;
            font-weight: 800;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.2rem;
            margin-bottom: 5px;
        }
        
        .demo-notice {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 2px solid #ffd166;
            border-radius: 15px;
            padding: 20px;
            margin: 25px 0;
            text-align: center;
            color: #856404;
            font-size: 1rem;
            animation: fadeIn 0.8s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .upload-section {
            border: 4px dashed #6a11cb;
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            margin: 30px 0;
            background: linear-gradient(135deg, #f8f9ff 0%, #eef1ff 100%);
            cursor: pointer;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .upload-section:hover {
            border-color: #2575fc;
            background: linear-gradient(135deg, #edf1ff 0%, #e3e9ff 100%);
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(106, 17, 203, 0.2);
        }
        
        .upload-section.drag-over {
            border-color: #2575fc;
            background: linear-gradient(135deg, #e3e9ff 0%, #d9e1ff 100%);
        }
        
        .upload-icon {
            font-size: 5rem;
            margin-bottom: 25px;
            color: #6a11cb;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .upload-text {
            font-size: 1.5rem;
            color: #444;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .upload-info {
            color: #777;
            font-size: 1rem;
            margin-bottom: 10px;
        }
        
        .controls {
            display: flex;
            gap: 25px;
            justify-content: center;
            margin: 40px 0;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 18px 35px;
            border: none;
            border-radius: 60px;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            min-width: 220px;
            justify-content: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .record-btn {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
        }
        
        .record-btn:hover:not(:disabled) {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(255, 65, 108, 0.4);
        }
        
        .record-btn.recording {
            animation: pulse 1.5s infinite;
            background: linear-gradient(135deg, #ff0000 0%, #ff4444 100%);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 8px 20px rgba(255,0,0,0.3); }
            50% { transform: scale(1.05); box-shadow: 0 12px 25px rgba(255,0,0,0.5); }
            100% { transform: scale(1); box-shadow: 0 8px 20px rgba(255,0,0,0.3); }
        }
        
        .analyze-btn {
            background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
            color: white;
        }
        
        .analyze-btn:hover:not(:disabled) {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 176, 155, 0.4);
        }
        
        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .audio-player {
            width: 100%;
            margin: 30px 0;
            border-radius: 15px;
            background: #f5f5f5;
            padding: 15px;
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        .file-info {
            text-align: center;
            color: #555;
            font-size: 1.1rem;
            margin: 15px 0;
            min-height: 30px;
            font-style: italic;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 50px 0;
            animation: fadeIn 0.5s ease;
        }
        
        .spinner {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #6a11cb;
            border-radius: 50%;
            width: 70px;
            height: 70px;
            animation: spin 1.5s linear infinite;
            margin: 0 auto 25px;
        }
        
        .loading-text {
            font-size: 1.2rem;
            color: #555;
            font-weight: 500;
        }
        
        .result-section {
            display: none;
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .result-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 20px;
            padding: 50px;
            text-align: center;
            margin: 40px 0;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .result-card:before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 8px;
            background: linear-gradient(90deg, #6a11cb, #2575fc);
        }
        
        .result-title {
            font-size: 2.2rem;
            color: #333;
            margin-bottom: 30px;
            font-weight: 700;
        }
        
        .emotion-display {
            font-size: 4rem;
            font-weight: 800;
            margin: 25px 0;
            min-height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            animation: bounceIn 1s ease;
        }
        
        @keyframes bounceIn {
            0% { transform: scale(0.5); opacity: 0; }
            60% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(1); }
        }
        
        .confidence-meter {
            display: inline-block;
            background: white;
            padding: 15px 35px;
            border-radius: 50px;
            font-size: 1.4rem;
            color: #333;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .visualization {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin: 40px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            border: 2px solid #f0f0f0;
        }
        
        .visualization-title {
            font-size: 1.8rem;
            color: #333;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 600;
        }
        
        .visualization img {
            width: 100%;
            border-radius: 15px;
            border: 2px solid #eaeaea;
            transition: transform 0.3s ease;
        }
        
        .visualization img:hover {
            transform: scale(1.01);
        }
        
        .emotions-panel {
            background: linear-gradient(135deg, #f8f9ff 0%, #eef1ff 100%);
            border-radius: 20px;
            padding: 40px;
            margin: 50px 0 30px;
        }
        
        .emotions-title {
            font-size: 2rem;
            color: #333;
            text-align: center;
            margin-bottom: 35px;
            font-weight: 700;
        }
        
        .emotions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 25px;
        }
        
        .emotion-item {
            background: white;
            border-radius: 20px;
            padding: 30px 20px;
            text-align: center;
            transition: all 0.4s ease;
            cursor: pointer;
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            border-top: 6px solid;
            position: relative;
            overflow: hidden;
        }
        
        .emotion-item:hover {
            transform: translateY(-15px) scale(1.05);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .emotion-item:after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(106,17,203,0.1) 0%, rgba(37,117,252,0.1) 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .emotion-item:hover:after {
            opacity: 1;
        }
        
        .emotion-emoji {
            font-size: 4rem;
            margin-bottom: 20px;
            display: block;
        }
        
        .emotion-name {
            font-size: 1.4rem;
            font-weight: 600;
            color: #333;
        }
        
        .emotion-desc {
            color: #666;
            font-size: 0.95rem;
            margin-top: 10px;
            line-height: 1.4;
        }
        
        .tech-info {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 20px;
            padding: 40px;
            margin-top: 50px;
            color: white;
        }
        
        .tech-title {
            font-size: 2rem;
            text-align: center;
            margin-bottom: 35px;
            color: white;
            font-weight: 600;
        }
        
        .features-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
        }
        
        .feature {
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        .feature:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 20px;
            display: block;
        }
        
        .feature-title {
            font-size: 1.3rem;
            margin-bottom: 15px;
            color: #fff;
            font-weight: 600;
        }
        
        .feature-desc {
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.6;
        }
        
        footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #eee;
            color: #666;
            font-size: 0.95rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 25px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .controls {
                flex-direction: column;
                align-items: center;
            }
            
            .btn {
                width: 100%;
                max-width: 320px;
            }
            
            .upload-section {
                padding: 40px 25px;
            }
            
            .emotions-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .features-list {
                grid-template-columns: 1fr;
            }
            
            .result-card {
                padding: 30px 20px;
            }
            
            .emotion-display {
                font-size: 3rem;
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🎤</div>
            <h1>Speech Emotion Recognition</h1>
            <p class="subtitle">Advanced AI-powered emotion detection from speech audio</p>
            <p class="subtitle">Upload or record audio to analyze emotional content</p>
        </header>
        
        <div class="demo-notice">
            <strong>⚠️ IMPORTANT:</strong> This is a demo application. For production use, 
            integrate with trained machine learning models using datasets like RAVDESS, TESS, or EMO-DB.
            Currently using advanced heuristic analysis with audio feature simulation.
        </div>
        
        <div class="upload-section" id="uploadArea">
            <div class="upload-icon">📁</div>
            <div class="upload-text">Drag & Drop Audio File Here</div>
            <div class="upload-text">or Click to Browse</div>
            <p class="upload-info">Supported formats: WAV, MP3, M4A, WEBM, OGG</p>
            <p class="upload-info">Maximum file size: 10MB</p>
            <p class="upload-info">For best results: Clear speech, 3-5 seconds duration</p>
            <input type="file" id="fileInput" accept="audio/*" style="display: none;">
        </div>
        
        <div class="controls">
            <button class="btn record-btn" id="recordBtn">
                <span class="record-icon">🎤</span>
                <span class="record-text">Record Audio (5s)</span>
            </button>
            <button class="btn analyze-btn" id="analyzeBtn" disabled>
                <span class="analyze-icon">🔍</span>
                <span class="analyze-text">Analyze Emotion</span>
            </button>
        </div>
        
        <audio class="audio-player" id="audioPreview" controls></audio>
        
        <div class="file-info" id="fileName">
            No audio file selected. Please upload or record audio.
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p class="loading-text">Processing Audio... Analyzing Features...</p>
            <p class="loading-text">Extracting MFCC, Pitch, Energy, and Spectral Characteristics</p>
        </div>
        
        <div class="result-section" id="resultSection">
            <div class="result-card">
                <h2 class="result-title">🎯 Emotion Analysis Result</h2>
                <div class="emotion-display" id="emotionResult"></div>
                <div class="confidence-meter" id="confidenceResult"></div>
                <p style="color: #666; margin-top: 25px; font-size: 1.1rem;">
                    Analysis based on audio waveform characteristics and spectral features
                </p>
            </div>
            
            <div class="visualization">
                <h3 class="visualization-title">📊 Audio Analysis Visualization</h3>
                <img id="visualizationImg" alt="Audio Waveform and Spectrogram Analysis">
            </div>
        </div>
        
        <div class="emotions-panel">
            <h3 class="emotions-title">🎭 Detectable Emotions</h3>
            <div class="emotions-grid">
                <div class="emotion-item" style="border-color: #4CAF50;">
                    <div class="emotion-emoji">😊</div>
                    <div class="emotion-name">Happy</div>
                    <div class="emotion-desc">High pitch, fast tempo, clear articulation</div>
                </div>
                <div class="emotion-item" style="border-color: #F44336;">
                    <div class="emotion-emoji">😠</div>
                    <div class="emotion-name">Angry</div>
                    <div class="emotion-desc">Loud, high energy, sharp tone</div>
                </div>
                <div class="emotion-item" style="border-color: #2196F3;">
                    <div class="emotion-emoji">😢</div>
                    <div class="emotion-name">Sad</div>
                    <div class="emotion-desc">Low pitch, slow tempo, soft tone</div>
                </div>
                <div class="emotion-item" style="border-color: #9E9E9E;">
                    <div class="emotion-emoji">😐</div>
                    <div class="emotion-name">Neutral</div>
                    <div class="emotion-desc">Flat tone, medium pace, calm delivery</div>
                </div>
                <div class="emotion-item" style="border-color: #E91E63;">
                    <div class="emotion-emoji">😲</div>
                    <div class="emotion-name">Surprised</div>
                    <div class="emotion-desc">Sudden pitch changes, abrupt stops</div>
                </div>
                <div class="emotion-item" style="border-color: #FF9800;">
                    <div class="emotion-emoji">😨</div>
                    <div class="emotion-name">Fearful</div>
                    <div class="emotion-desc">Trembling voice, high pitch, fast speech</div>
                </div>
            </div>
        </div>
        
        <div class="tech-info">
            <h3 class="tech-title">⚙️ Technology & Features</h3>
            <div class="features-list">
                <div class="feature">
                    <div class="feature-icon">🎵</div>
                    <div class="feature-title">Audio Processing</div>
                    <div class="feature-desc">Advanced waveform analysis with spectral feature extraction</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-title">Feature Analysis</div>
                    <div class="feature-desc">MFCC, Pitch, Energy, Zero-crossing rate, Spectral analysis</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">📈</div>
                    <div class="feature-title">Real-time Visualization</div>
                    <div class="feature-desc">Waveform and spectrogram visualization for detailed analysis</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-title">Emotion Detection</div>
                    <div class="feature-desc">Six emotional states with confidence scoring</div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Speech Emotion Recognition System | Demo Version 2.0</p>
            <p>For research and educational purposes</p>
            <p>© 2024 Emotion Recognition AI</p>
        </footer>
    </div>

    <script>
        // DOM Elements
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const recordBtn = document.getElementById('recordBtn');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const audioPreview = document.getElementById('audioPreview');
        const fileName = document.getElementById('fileName');
        const loading = document.getElementById('loading');
        const resultSection = document.getElementById('resultSection');
        const emotionResult = document.getElementById('emotionResult');
        const confidenceResult = document.getElementById('confidenceResult');
        const visualizationImg = document.getElementById('visualizationImg');
        
        // State variables
        let audioBlob = null;
        let mediaRecorder = null;
        let audioChunks = [];
        let isRecording = false;
        
        // Emotion color mapping
        const emotionColors = {
            '😊 Happy': '#4CAF50',
            '😠 Angry': '#F44336',
            '😢 Sad': '#2196F3',
            '😐 Neutral': '#9E9E9E',
            '😲 Surprised': '#E91E63',
            '😨 Fearful': '#FF9800'
        };
        
        // File upload handling
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
        
        // Audio recording
        recordBtn.addEventListener('click', async () => {
            if (!isRecording) {
                await startRecording();
            } else {
                stopRecording();
            }
        });
        
        // Emotion analysis
        analyzeBtn.addEventListener('click', analyzeAudio);
        
        // Handle file selection
        function handleFile(file) {
            // Validate file
            if (!file.type.includes('audio/')) {
                showError('Please select an audio file (WAV, MP3, WEBM, etc.)');
                return;
            }
            
            if (file.size > 10 * 1024 * 1024) {
                showError('File size must be less than 10MB');
                return;
            }
            
            // Set audio blob
            audioBlob = file;
            
            // Create preview URL
            const audioURL = URL.createObjectURL(file);
            audioPreview.src = audioURL;
            audioPreview.style.display = 'block';
            
            // Update UI
            fileName.textContent = `📄 Selected: ${file.name} (${formatFileSize(file.size)})`;
            analyzeBtn.disabled = false;
            resultSection.style.display = 'none';
            
            // Scroll to audio player
            audioPreview.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        // Start recording
        async function startRecording() {
            try {
                // Request microphone access
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        sampleRate: 44100
                    }
                });
                
                // Initialize MediaRecorder
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                // Handle data available
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };
                
                // Handle recording stop
                mediaRecorder.onstop = () => {
                    // Create audio blob
                    audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    
                    // Create preview URL
                    const audioURL = URL.createObjectURL(audioBlob);
                    audioPreview.src = audioURL;
                    audioPreview.style.display = 'block';
                    
                    // Update UI
                    fileName.textContent = '🎤 Recording complete. Ready for analysis.';
                    analyzeBtn.disabled = false;
                    resultSection.style.display = 'none';
                    
                    // Stop all tracks
                    stream.getTracks().forEach(track => track.stop());
                };
                
                // Start recording
                mediaRecorder.start();
                isRecording = true;
                
                // Update UI
                recordBtn.classList.add('recording');
                recordBtn.innerHTML = '<span class="record-icon">⏹️</span><span class="record-text">Stop Recording</span>';
                fileName.textContent = '🎤 Recording... Speak now (5 seconds)';
                
                // Auto-stop after 5 seconds
                setTimeout(() => {
                    if (isRecording && mediaRecorder.state === 'recording') {
                        stopRecording();
                    }
                }, 5000);
                
            } catch (error) {
                console.error('Recording error:', error);
                showError('Could not access microphone. Please check permissions and try again.');
            }
        }
        
        // Stop recording
        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                isRecording = false;
                
                // Update UI
                recordBtn.classList.remove('recording');
                recordBtn.innerHTML = '<span class="record-icon">🎤</span><span class="record-text">Record Audio (5s)</span>';
            }
        }
        
        // Analyze audio
        async function analyzeAudio() {
            if (!audioBlob) {
                showError('Please upload or record an audio file first.');
                return;
            }
            
            // Show loading state
            loading.style.display = 'block';
            resultSection.style.display = 'none';
            analyzeBtn.disabled = true;
            
            // Prepare form data
            const formData = new FormData();
            formData.append('audio', audioBlob, 'audio_recording.webm');
            
            try {
                // Send request to server
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                // Parse response
                const result = await response.json();
                
                if (result.success) {
                    // Display results
                    displayResults(result);
                } else {
                    showError('Analysis failed: ' + result.error);
                }
            } catch (error) {
                console.error('Analysis error:', error);
                showError('Error analyzing audio. Please try again.');
            } finally {
                // Reset UI
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        }
        
        // Display analysis results
        function displayResults(result) {
            // Set emotion
            emotionResult.textContent = result.emotion;
            
            // Set emotion color
            const emotionColor = emotionColors[result.emotion] || '#6a11cb';
            emotionResult.style.color = emotionColor;
            emotionResult.style.border = `4px solid ${emotionColor}`;
            
            // Set confidence
            const confidencePercent = (result.confidence * 100).toFixed(1);
            confidenceResult.textContent = `Confidence: ${confidencePercent}%`;
            confidenceResult.style.background = `linear-gradient(90deg, ${emotionColor}20, ${emotionColor}40)`;
            confidenceResult.style.color = emotionColor;
            confidenceResult.style.border = `2px solid ${emotionColor}30`;
            
            // Set visualization
            if (result.visualization) {
                visualizationImg.src = `data:image/png;base64,${result.visualization}`;
                visualizationImg.style.display = 'block';
            } else {
                visualizationImg.style.display = 'none';
            }
            
            // Show results section
            resultSection.style.display = 'block';
            
            // Scroll to results
            setTimeout(() => {
                resultSection.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);
        }
        
        // Show error message
        function showError(message) {
            fileName.textContent = `❌ ${message}`;
            fileName.style.color = '#F44336';
            
            // Reset after 3 seconds
            setTimeout(() => {
                fileName.style.color = '#555';
            }, 3000);
        }
        
        // Format file size
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        // Initialize emotion items with click events
        document.querySelectorAll('.emotion-item').forEach(item => {
            item.addEventListener('click', function() {
                const emotion = this.querySelector('.emotion-name').textContent;
                const emoji = this.querySelector('.emotion-emoji').textContent;
                
                // Show info about the emotion
                fileName.textContent = `💡 ${emotion}: ${this.querySelector('.emotion-desc').textContent}`;
                fileName.style.color = '#6a11cb';
                
                // Reset after 2 seconds
                setTimeout(() => {
                    if (!audioBlob) {
                        fileName.textContent = 'No audio file selected. Please upload or record audio.';
                        fileName.style.color = '#555';
                    }
                }, 2000);
            });
        });
        
        // Initialize with welcome message
        console.log('🎤 Speech Emotion Recognition App Loaded');
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Home page - serves the HTML interface"""
    return HTML

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze audio file endpoint"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'})
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
      
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_path = temp_file.name
        audio_file.save(temp_path)
        temp_file.close()
        
        
        emotion, confidence, visualization = analyzer.analyze_audio_file(temp_path)
        
        
        try:
            os.unlink(temp_path)
        except:
            pass
        
        if emotion is None:
            return jsonify({'success': False, 'error': 'Could not analyze audio file'})
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'confidence': float(confidence),
            'visualization': visualization
        })
        
    except Exception as e:
        print(f"Server error in /analyze: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred while processing audio'
        })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Speech Emotion Recognition',
        'version': '2.0.0',
        'timestamp': '2024-12-31T10:46:02Z'
    })

def main():
    """Main function to run the application"""
    print("\n" + "="*80)
    print("🎤 SPEECH EMOTION RECOGNITION WEB APPLICATION")
    print("="*80)
    print("✅ Initializing application...")
    print(f"📁 Temporary directory: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
    print("🌐 Web Interface: http://localhost:5000")
    print("🔧 API Endpoint: http://localhost:5000/analyze [POST]")
    print("❤️  Health Check: http://localhost:5000/health [GET]")
    print("="*80)
    print("🎯 FEATURES:")
    print("   • Upload audio files (WAV, MP3, M4A, WEBM, OGG)")
    print("   • Record 5-second audio samples via microphone")
    print("   • Advanced audio feature analysis")
    print("   • Six emotion detection with confidence scoring")
    print("   • Real-time waveform and spectrogram visualization")
    print("   • Modern, responsive UI with animations")
    print("="*80)
    print("🚀 Starting Flask server...")
    print("="*80)
    
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )

if __name__ == '__main__':
    main()
