# Embedding the Model in Drones and Cameras

This guide describes how to integrate the InspAI structural damage model with **drones** and **cameras**. For who the project is for (civil engineers, architects, inspectors) and how damage descriptions and labels are used (e.g. labeling critical buildings), see [AUDIENCE_AND_USE_CASES.md](AUDIENCE_AND_USE_CASES.md) and [TERMINOLOGY_AND_LABELS.md](TERMINOLOGY_AND_LABELS.md). where the model runs, how images are captured and sent, and how to implement each option step by step.

---

## Overview: Two ways to embed

| Approach | Where the model runs | Where capture runs | Best for |
|----------|----------------------|--------------------|----------|
| **1. API (cloud or edge server)** | Your server (GPU) running `run_api.py` | Drone or camera device sends images to the API | Easiest; works with any drone/camera that can HTTP. |
| **2. On-device** | Same hardware as the camera (e.g. Jetson, companion PC) | Same device runs capture + model | No network dependency; real-time on the device. |

In both cases the **same model** (LLaVA-1.5-7B) and the **same API contract** apply: input = image (file or base64), output = `damage_description`. For on-device you either run the same API locally or call the model directly (e.g. via `structural_damage_model` inference scripts).

---

## Part 1: Drone integration

### 1.1 Architecture options

- **A. Drone → images to your API (recommended to start)**  
  Drone (or ground station) captures photos; a small app on a companion device or ground station sends each image to `POST /v1/analyze` with `source_type=drone`. The model runs on your server (or an edge box with GPU).

- **B. Drone with companion computer (on-device)**  
  A Jetson or similar board on the drone runs the camera and the model (or a local instance of this API). No need to stream raw video to the cloud; only results (e.g. damage descriptions) are sent if needed.

### 1.2 Option A: Drone sends images to the API

**Requirements**

- Drone that can save still images (e.g. DJI, PX4 with camera trigger, or manual capture).
- A device that can run Python and HTTP (companion computer on the drone, or ground station laptop/Raspberry Pi).
- Your InspAI API reachable from that device (same network or public URL).

**Step 1: Get images from the drone**

- **DJI (e.g. Mavic, Matrice):** Use DJI SDK (MSDK or PSDK) to trigger still capture and download photos to the companion device or to the ground station after landing.
- **PX4 / MAVLink:** Use camera trigger (MAV_CMD_IMAGE_START_CAPTURE) and then retrieve images via FTP or storage mounted on the companion computer.
- **Generic:** If the drone saves to an SD card or streams to a ground station, copy the image files to the machine that will call the API.

**Step 2: Call the API from the capture device**

On the device that has the image files (or receives them from the drone), use the same API as for any other client: `POST /v1/analyze` with the image and `source_type=drone`.

Example (Python on companion PC or ground station):

```python
import requests
from pathlib import Path

API_URL = "http://YOUR_SERVER:8000/v1/analyze"  # or your edge server

def analyze_drone_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        r = requests.post(
            API_URL,
            files={"file": (Path(image_path).name, f)},
            data={"source_type": "drone"},
        )
    r.raise_for_status()
    return r.json()["results"][0]["damage_description"]

# After each capture (e.g. in a loop or callback):
description = analyze_drone_image("/path/to/captured_photo.jpg")
print(description)
```

**Step 3: Batch after a flight**

If you collect many images during a flight, send them in one request with `POST /v1/analyze/batch` (see [API.md](API.md)) so the server processes them in one go. Use `source_type=drone` for all.

### 1.3 Option B: Run the model on the drone (companion computer)

**Requirements**

- Companion computer with enough RAM and, for LLaVA-1.5-7B, a GPU (e.g. **NVIDIA Jetson Orin**). On weaker hardware (e.g. Jetson Nano) you may need a smaller model or quantization.
- Camera connected to this computer (USB, CSI, or via drone SDK).
- Same repo (or API server) running on the companion: install dependencies and either run `run_api.py` locally or call the inference script directly.

**Step 1: Install on the companion computer**

- Flash the board (e.g. JetPack for Jetson).
- Install Python 3, pip, and CUDA if using GPU.
- Clone the repo and install: `pip install -r requirements-api.txt` (and optionally run the model in mock mode first to verify the stack).

**Step 2: Run the API locally**

- Start the API on the companion: `python run_api.py` (or `uvicorn api.app:app --host 0.0.0.0 --port 8000`). The model runs on this device; no internet required for inference.
- Use `STRUCTURE_API_MODEL_NAME` if you have a quantized or smaller checkpoint for the Jetson.

**Step 3: Capture and analyze on the same device**

- From the same machine, capture frames (e.g. from the drone camera via SDK or a USB/CSI camera).
- For each captured image, call `http://127.0.0.1:8000/v1/analyze` with `source_type=drone` (same Python snippet as in 1.2). Optionally run capture and HTTP client in separate processes (e.g. one script captures and writes images, another watches a folder and sends them to localhost API).

**Step 4: Reduce latency and load (optional)**

- Use a smaller or quantized model (e.g. 4-bit) so LLaVA fits and runs on the Jetson.
- Trigger capture only at waypoints or at a fixed interval to avoid overloading the device.

---

## Part 2: Camera integration

### 2.1 Architecture options

- **A. Camera → images to your API**  
  A device (Raspberry Pi, NVR, PC) that has access to the camera (IP, RTSP, USB) captures frames and sends them to your InspAI API. The model runs on the server.

- **B. Camera + edge device (on-device)**  
  A Jetson, Raspberry Pi (with Coral or small model), or other edge box runs the camera and the model (or a local API instance). Good for offline or low-latency use.

### 2.2 Option A: Camera streams or snapshots to the API

**Requirements**

- A camera (IP, RTSP, USB, or built-in) and a machine that can read from it (Raspberry Pi, Linux PC, NVR).
- Your InspAI API reachable from that machine.

**Step 1: Capture frames from the camera**

- **IP / RTSP camera:** Use OpenCV or GStreamer to open the stream and grab frames (e.g. on a timer or on motion).
- **USB camera:** Same with OpenCV (`cv2.VideoCapture`) or `v4l2`/GStreamer.

Example (OpenCV, save a frame and then call API):

```python
import cv2
import requests
import tempfile
import os

API_URL = "http://YOUR_SERVER:8000/v1/analyze"
CAMERA_URL = 0  # or "rtsp://user:pass@ip:554/stream", or IP camera URL

cap = cv2.VideoCapture(CAMERA_URL)
_, frame = cap.read()
cap.release()

if frame is not None:
    path = tempfile.mktemp(suffix=".jpg")
    cv2.imwrite(path, frame)
    with open(path, "rb") as f:
        r = requests.post(API_URL, files={"file": f}, data={"source_type": "inspection"})
    print(r.json()["results"][0]["damage_description"])
    os.remove(path)
```

**Step 2: Run periodically or on demand**

- **Periodic:** A cron job or a loop (e.g. every 30 s) captures one frame and sends it to the API; store or display the returned `damage_description`.
- **On demand:** A button or HTTP trigger on your app captures one frame and calls the API.
- **Batch:** Capture N frames (e.g. one per minute), then send them with `POST /v1/analyze/batch` and `source_type=inspection` (or `google_maps` if from a static map camera).

**Step 3: Use base64 if you prefer**

If you don’t want to write a file, encode the frame as base64 and send it in the `image_base64` form field (see [API.md](API.md)). Same endpoint, same response.

### 2.3 Option B: Run the model on the camera device (edge)

**Requirements**

- Edge device with the camera (e.g. Jetson Nano/Orin, Raspberry Pi 4 + Coral, or a small PC). LLaVA-1.5-7B needs a capable GPU (e.g. Jetson Orin); for RPi you’d need a much smaller model or only the API client (Option A).
- Same repo and dependencies on the device if you run the API there.

**Step 1: Install and run the API on the edge device**

- On the device: clone repo, `pip install -r requirements-api.txt`, then run `python run_api.py` (optionally with a quantized/smaller `STRUCTURE_API_MODEL_NAME` for Jetson).
- The camera and the API run on the same machine; no external server needed for inference.

**Step 2: Capture and call localhost**

- From the same device, capture from the camera (OpenCV, GStreamer, or vendor SDK).
- Call `http://127.0.0.1:8000/v1/analyze` with the captured image (file or base64) and `source_type=inspection` (or `drone` if it’s a drone camera). Use the same Python snippet as in 2.2 but with `API_URL = "http://127.0.0.1:8000/v1/analyze"`.

**Step 3: Integrate with your app**

- Your app (web, mobile, or desktop) can call the edge device’s IP and port (e.g. `http://192.168.1.10:8000/v1/analyze`) so the camera device acts as the “model server” for your LAN.

---

## Part 3: Summary and checklist

| Goal | Suggested approach |
|------|---------------------|
| Drone photos analyzed in the cloud or on a server | Drone/companion or ground station sends images to your API (Option A). |
| Drone with no reliable link; analyze on board | Run API (or inference) on companion computer; capture and call localhost (Option B). |
| IP/RTSP/USB camera analyzed on a server | Device that sees the camera captures frames and sends to your API (Option A). |
| Camera and model on the same box (offline/low latency) | Run API on the same device as the camera; capture and call localhost (Option B). |

**Checklist for embedding**

1. **API is running** (cloud, edge, or local): `python run_api.py` and `GET /health` returns OK.
2. **Images** are available as files or in-memory (OpenCV frame → encode or save).
3. **Client** sends each image to `POST /v1/analyze` (or batch to `POST /v1/analyze/batch`) with the correct `source_type` (`drone` | `google_maps` | `inspection`).
4. **Response** is parsed for `results[].damage_description` (and optionally `labels` later).

For exact request/response format, authentication, and rate limits, see [API.md](API.md). For training your own model and serving it via the same API, see [DEPLOYMENT.md](DEPLOYMENT.md).
