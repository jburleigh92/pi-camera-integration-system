# Pi Camera Integration System  
Automated Image Capture + Reliability Testing Pipeline  
-----------------------------------------------------

This project implements a hardware–software integration system using a **Raspberry Pi 4** and a **USB webcam**.  
Its purpose is to simulate a real-world industrial imaging pipeline:  
capturing images on schedule, handling unpredictable hardware behavior,  
logging failures, and maintaining long-running stability.

The system uses:

- **Linux V4L2 driver stack**  
- **fswebcam** for frame acquisition  
- **Python orchestration layer** for retries, logging, device checks  
- **Structured folder layout** to follow industry engineering practices  

The project is designed to mirror integration workflows at companies like  
**Mycronic, Outpost, SpaceX, Shift5, Tesla, and other robotics / automation teams**.

---

## 🎯 Project Goals

- Provide a working example of **hardware–software integration**
- Demonstrate **system reliability practices** (retry logic, health checks)
- Test real-world failure modes (disconnects, timeouts, corrupted frames)
- Create production-style **documentation and observability**
- Show engineering structure suitable for a Systems Integration role

---

## 🏗 System Architecture

### **High-Level Architecture**

```
+————————————————————————————————————————+
|           Hardware Layer                |
|  Raspberry Pi 4  <–– USB ––>  Webcam   |
+————————————————+———————————————————————+
                 |
            V4L2 USB Drivers
                 |
+————————————————+———————————————————————+
|        Device Interface Layer           |
|      /dev/video0 (camera node)         |
+————————————————+———————————————————————+
                 |
            fswebcam CLI
                 |
+————————————————+———————————————————————+
|       Application Layer (Python)        |
|   - Capture loop                        |
|   - Retry engine                        |
|   - Warm-up logic                       |
|   - Logging                             |
|   - Disconnect detection                |
+————————————————+———————————————————————+
                 |
         Image Files + Log Files
```

---

## 📂 Folder Structure

```
pi-camera-integration-system/
│
├── src/
│   ├── app/
│   │   ├── capture.py
│   │   ├── camera_interface.py
│   │   ├── health_check.py
│   │   ├── config.py
│   │   └── __init__.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── file_manager.py
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── tests/
│   ├── test_capture_flow.md
│   ├── failure_simulations.md
│   └── stress_test_results.md
│
├── docs/
│   ├── architecture.md
│   ├── data_flow.md
│   ├── troubleshooting.md
│   ├── setup_instructions.md
│   ├── hardware_overview.md
│   └── roadmap.md
│
├── logs/
│   └── capture_log.txt
│
├── captures/
│
├── config/
│   └── default_config.yaml
│
├── scripts/
│   ├── install_dependencies.sh
│   ├── start.sh
│   ├── stop.sh
│   └── run_once.sh
│
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔌 Hardware Requirements

- Raspberry Pi 4  
- USB Webcam (any V4L2-compatible device)  
- MicroSD card  
- Power supply  
- Internet connection (for package installs)  

Optional:

- DSLR camera (gPhoto2 integration for advanced workflows)

---

## 🛠 Software Requirements

- Raspberry Pi OS **Bullseye (Legacy)**
- Python 3.x  
- fswebcam  
- Bash shell  
- Optional: OpenCV, gPhoto2  

Install core tools:

```bash
sudo apt update
sudo apt install fswebcam python3-pip -y
```

---

## 🚀 How It Works

### 1. Camera Validation

The system checks:
- `/dev/video0` exists
- V4L2 can access the device
- Warm-up delay is respected

### 2. Image Capture

Images are captured via:

```bash
fswebcam --no-banner output.jpg
```

The Python system wraps this in:
- retries
- timeouts
- logging

### 3. Error Handling

The system gracefully handles:
- device disconnects
- driver timeouts
- corrupted output
- "device busy" states
- low-light frames

### 4. Long-Running Stability

A scheduler captures images every N seconds while tracking:
- success rate
- failure rate
- time between errors
- system health trends

---

## 📑 Example Log Output

```
[2025-01-10 14:03:22] SUCCESS: Captured img_20250110_140322.jpg
[2025-01-10 14:03:32] ERROR: Capture failed (device busy). Retrying (1/3)
[2025-01-10 14:03:34] SUCCESS: Recovery successful after retry
[2025-01-10 14:05:01] ERROR: Camera disconnected!
```

---

## 🧪 Testing & Failure Simulation

Documented in `tests/`:

**Included Scenarios:**
- Unplug camera mid-capture
- Reconnect camera during active session
- Reduce USB power
- Stress test (1–2 hours continuous capture)
- Deliberate overexposure / underexposure
- Intentional timeouts

Each scenario includes expected behavior and actual results.

---

## 📚 Documentation Included

All docs live in the `docs/` folder:
- `architecture.md` → high-level diagrams & subsystems
- `data_flow.md` → capture → storage → logging pipeline
- `troubleshooting.md` → common errors + fixes
- `setup_instructions.md` → how to deploy on a fresh Pi
- `hardware_overview.md` → camera and Pi specifications
- `roadmap.md` → planned improvements

---

## 🔮 Roadmap / Future Enhancements

- Replace fswebcam with OpenCV capture backend
- Add DSLR support via gphoto2
- Add Kafka/MQTT to stream images
- Add health dashboard with real-time metrics
- Add watchdog service for auto-restart on failure
- Add ML-based image quality scoring

---

## 📝 License

MIT License – free for use, modification, and distribution.

---

## 👤 Author

**Jason Burleigh**  
Systems Integration Engineer – Demonstration Project  
2025

**This will impress Mycronic.**
