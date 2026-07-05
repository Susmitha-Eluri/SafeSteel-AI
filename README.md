# SafeSteel-AI
SafeSteel-AI is an intelligent, edge-integrated Computer Vision and Automated Safety Shield designed for Steel Melting Shops (SMS). By repurposing standard facility CCTV feeds into active digital supervisors, the system automatically detects structural non-compliance, prevents workers from skipping dangerous chemical degassing time.

# 🏗️ SafeSteel-AI: Intelligent Steel Melting Shop Guardian

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![YOLOv8](https://img.shields.io/badge/Ultralytics-YOLOv8-success.svg)](https://ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-orange.svg)](https://opencv.org/)

SafeSteel-AI is a real-time Computer Vision and Edge AI system engineered for heavy metallurgical environments (Steel Melting Shops). Inspired by forensic industrial accident analyses—specifically targeting catastrophic ladle gas explosion mechanics—SafeSteel-AI acts as an automated behavioral and process safety shield to drop operational fatalities to zero.

---

## 🎯 The Problem Statement
Traditional heavy manufacturing facilities rely entirely on manual oversight and paper-based Standard Operating Procedures (SOPs). In high-stress, understaffed industrial environments, critical safety steps can be skipped. When a 150-tonne ladle carrying molten steel at 1,500°C experiences a sudden chemical or mechanical failure, nearby workers are left with zero reaction time, resulting in catastrophic loss of life.

**SafeSteel-AI solves this by converting passive CCTV infrastructure into an active digital supervisor and machine-interlock gatekeeper.**

---

## 🛠️ System Architecture & Core Pillars

The solution operates on a strict **Multi-Modal Safety State Machine** addressing three critical industrial failure vectors:

                     ┌────────────────────────────────────────┐
                     │       SAFESTEEL-AI ACTIVE SHIELD       │
                     └────────────────────────────────────────┘
                                      │
   ┌────────────────────────==========┼============────────────────────────┐
   ▼                                  ▼                                    ▼
1. **Pillar 1: Structural Non-Compliance Detection:** Uses visual object confirmation to verify that mandatory ladle thermal safety covers are securely attached before transport.
2. **Pillar 2: Process-Skipping Watchdog:** Employs temporal state tracking to act as an un-bypassable countdown clock, ensuring liquid steel undergoes its full mandatory Argon Rinsing duration to vent entrapped gases.
3. **Pillar 3: Ultra-Sensitive Proximity Protection:** Uses a pre-trained `YOLOv8-Nano` model combined with geometric intersection algorithms (`cv2.pointPolygonTest`). Rather than waiting for a worker's full body to enter the danger zone, the system calculates a multi-vertex box model—**tripping a hard machine lockout the instant a single limb crosses the hazard threshold.**

---
## 🚀 Quick Start & Installation

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed on your environment.

### 2. Clone and Setup
```bash
# Clone the repository
git clone [https://github.com/yourusername/safesteel-ai.git](https://github.com/yourusername/safesteel-ai.git)
cd safesteel-ai

# Install core dependencies
pip install -r requirements.txt

## 💻 Technical Deep-Dive & Code Architecture

### 1. Frontend / UI Layer
* **Streamlit:** Used as the rapid-prototyping web framework to build the dashboard interface entirely in Python.
* **Custom CSS (HTML/CSS Injection):** Injected directly into Streamlit to override default styles, providing the premium dark theme, glassmorphism UI elements, pulsing `@keyframes` animations, and modern Google Fonts (Orbitron & Inter).

### 2. Computer Vision & Edge AI
* **YOLOv8 (by Ultralytics):** The state-of-the-art, real-time object detection model. We used the `yolov8n.pt` (nano) model for its speed on edge devices. It handles the continuous bounding-box detection of workers, the ladle, and the cover.
* **OpenCV (opencv-python):** Handles the video stream processing and all spatial/geometric math. Specifically, we leveraged OpenCV's `cv2.pointPolygonTest` algorithm to calculate the ray-casting math that determines if a worker's bounding box intersects with the geofenced hazard polygon.

### 3. Backend Logic & Runtime
* **Python 3.x:** The core programming language tying everything together (state management, timers, interlock logic).
* **NumPy:** Used heavily behind the scenes by OpenCV and YOLOv8 for fast array computations, particularly when transforming bounding box coordinates for the polygon intersection logic.

