# Surveillance Computer Vision System

A comprehensive real-time surveillance system using advanced computer vision and deep learning models for object detection, tracking, face recognition, and alert generation.

## 🎯 Features

- **Real-time Object Detection & Tracking**: YOLOv8 + DeepSORT for accurate object detection and multi-object tracking
- **Low-light Enhancement**: Zero-DCE for automatic low-light image enhancement
- **Scene Understanding**: Mask2Former for semantic segmentation + ResNet for feature extraction
- **Face Recognition**: MTCNN face detection → GAN enhancement → FaceNet embeddings for identity matching
- **Alert System**: Three types of alerts:
  - **Stationary/Loitering**: Detects persons staying in one place for extended periods
  - **Restricted Zone**: Monitors predefined restricted areas
  - **Unknown Person**: Identifies unrecognized individuals
- **Email Notifications**: Automatic email alerts sent to configured recipients
- **Database Storage**: SQLite database for storing alerts and person information
- **Web Interface**: FastAPI-based web interface with real-time video feed and database viewer

## 📋 Pipeline Flow

```
Frame Input
    ↓
Zero-DCE (low-light enhancement - conditional)
    ↓
YOLOv8 (object detection)
    ↓
DeepSORT (track IDs) ← 🔴 OUTPUT 1: Real-time Display
    ↓
Mask2Former (scene/zone semantics)
    ↓
ResNet (scene/object context features) ← 📊 OUTPUT 2: Scene Understanding
    ↓
[IF class == person]
    ↓
MTCNN (face detection)
    ↓
Crop Face
    ↓
GAN (face enhancement - optional)
    ↓
FaceNet (embeddings → identity)
    ↓
Alert Engine (stationary, restricted zone, unknown person)
    ↓
Database + Email
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (optional, but recommended for better performance)
- Webcam or video file

### Installation

1. **Clone or navigate to the project directory**

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download YOLOv8 weights** (if not already present)
   - The system will automatically download `yolov8n.pt` on first run

### Running the Pipeline

#### Option 1: Command Line (Recommended)

**Using webcam:**
```bash
python run_pipeline.py --source 0 --camera-id CAM_01
```

**Using video file:**
```bash
python run_pipeline.py --source "sample.mp4" --camera-id CAM_01
```

**Using different camera index:**
```bash
python run_pipeline.py --source 1 --camera-id CAM_01
```

#### Option 2: Web Interface

**Start FastAPI server:**
```bash
uvicorn app.app:app --reload
```

**Access in browser:**
- Main page: `http://localhost:8000/`
- Database viewer: `http://localhost:8000/database`

### Controls

- Press `q` or `ESC` to quit the pipeline
- The system displays real-time output with bounding boxes, track IDs, and alerts

## 📁 Project Structure

```
survillance_computerVision_Project/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── app.py                    # FastAPI web application
│   ├── full_pipeline.py          # Main pipeline orchestration
│   ├── models_loader.py          # Model loading utilities
│   ├── run_pipeline.py           # Command-line runner
│   ├── video_processsor.py       # Video processing utilities
│   ├── models/                   # Model implementations
│   │   ├── yolo.py              # YOLOv8 detection
│   │   ├── deepsort.py          # DeepSORT tracking
│   │   ├── mask2former.py       # Mask2Former segmentation
│   │   ├── resnet.py            # ResNet feature extraction
│   │   ├── mtcnn.py             # MTCNN face detection
│   │   ├── gan_sr.py            # GAN face enhancement
│   │   ├── facenet.py           # FaceNet embeddings
│   │   └── zeroDce.py           # Zero-DCE low-light enhancement
│   └── pipelines/               # Processing pipelines
│       ├── detect_n_track.py    # Detection + tracking
│       ├── scene_understanding.py # Scene analysis
│       ├── face_pipeline.py      # Face processing
│       ├── face_matcher.py      # Face matching logic
│       ├── db_writer.py         # Database operations
│       └── email_service.py     # Email notifications
├── alerts/                       # Alert generation
│   ├── alerts.py                # Main alert engine
│   ├── stationary.py            # Stationary detection
│   └── zone_check.py            # Restricted zone checking
├── utils/                        # Utilities
│   ├── db.py                    # Database models
│   └── lowlight.py              # Low-light detection
├── templates/                    # HTML templates
│   ├── index.html              # Main web interface
│   └── database.html            # Database viewer
├── static/                      # Static files
│   └── css/
│       └── style.css           # Stylesheet
├── requirements.txt             # Python dependencies
├── run_pipeline.py             # Root-level runner
├── test_camera_detailed.py     # Camera testing utility
└── README.md                    # This file
```

## ⚙️ Configuration

### Email Configuration

Edit `app/pipelines/email_service.py` to configure email settings:

```python
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"  # Gmail App Password
EMAIL_RECEIVER = "recipient@gmail.com"
```

**Note**: For Gmail, you need to generate an App Password:
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"

### Restricted Zones

Edit `alerts/zone_check.py` to define restricted zones:

```python
RESTRICTED_ZONES = {
    "CAM_01": [
        shapely.geometry.Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    ]
}
```

### Database

The system uses SQLite database (`surveillance.db`) by default. Database tables are automatically created on first run.

**Tables:**
- `persons`: Registered persons with face embeddings
- `alerts`: Generated alerts with timestamps

## 🔍 Testing

### Test Camera Access

```bash
python test_camera_detailed.py
```

This will test different camera indices and backends to find working cameras.

### Test Email Service

```bash
python -c "from app.pipelines.email_service import send_email; send_email('Test', 'Test message')"
```

### View Database

**Option 1: Web Interface**
```bash
uvicorn app.app:app --reload
# Then visit http://localhost:8000/database
```

**Option 2: Python Script**
```python
from utils.db import SessionLocal, Alert, Person

db = SessionLocal()
alerts = db.query(Alert).all()
for alert in alerts:
    print(f"{alert.id}: {alert.alert_type} - {alert.description} - {alert.created_at}")
db.close()
```

**Option 3: SQLite Command Line**
```bash
sqlite3 surveillance.db
.tables
SELECT * FROM alerts;
SELECT * FROM persons;
```

## 🐛 Troubleshooting

### Camera Issues

**Problem**: Cannot open camera

**Solutions**:
1. Close all applications using the camera (Zoom, Teams, Skype, etc.)
2. Check Windows camera permissions
3. Try different camera indices: `--source 1`, `--source 2`
4. Use a video file instead: `--source "video.mp4"`

### Model Loading Errors

**Problem**: Models fail to load

**Solutions**:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`
3. Some models are optional (Zero-DCE, GAN) - the system will continue without them

### Email Not Sending

**Problem**: Email alerts not received

**Solutions**:
1. Verify email credentials in `app/pipelines/email_service.py`
2. Check Gmail App Password is correct
3. Test email service manually (see Testing section)
4. Check console for error messages

### Performance Issues

**Problem**: Slow processing

**Solutions**:
1. Use GPU if available (CUDA)
2. Reduce video resolution in `app/run_pipeline.py`
3. Adjust frame skip rate for heavy models (currently every 15 frames)
4. Disable optional models (Zero-DCE, GAN) if not needed

## 📊 Outputs

### OUTPUT 1: Real-time Display
- Displayed immediately after DeepSORT tracking
- Shows bounding boxes, track IDs, class labels, and confidence scores
- Alerts displayed on frame
- Scene features indicator

### OUTPUT 2: Scene Understanding
- Generated every 15 frames for performance
- ResNet features for scene context
- Mask2Former segmentation for zone semantics
- Printed to console and displayed on frame

## 📝 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📧 Support

For issues or questions, please check the troubleshooting section or create an issue in the repository.

---

**Note**: This system is designed for surveillance and security applications. Ensure compliance with local privacy laws and regulations when deploying.
