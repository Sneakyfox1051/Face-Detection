# Database Viewer Guide

## ✅ Database Viewer Created!

A web interface has been added to view your surveillance database.

## How to Access

### 1. Start the FastAPI Server
```bash
uvicorn app.app:app --reload
```

### 2. Open in Browser
Navigate to:
```
http://localhost:8000/database
```

## Features

### 📊 Statistics Dashboard
- **Total Alerts**: Count of all alerts in database
- **Registered Persons**: Number of known persons
- **Stationary Alerts**: Loitering detection count
- **Restricted Zone**: Zone violation count
- **Unknown Persons**: Unrecognized person count

### 📋 Alerts Table
- View all alerts with details:
  - Alert ID
  - Timestamp
  - Alert Type (color-coded)
  - Camera ID
  - Track ID
  - Description

### 🔍 Filtering Options
- **Filter by Alert Type**: Stationary, Restricted Zone, Unknown Person
- **Filter by Camera**: CAM_01, etc.
- **Refresh Button**: Manually reload data
- **View Persons**: Switch to persons view

### 🔄 Auto-Refresh
- Statistics and alerts update every 5 seconds automatically

## API Endpoints

You can also access the data via API:

### Get Alerts
```
GET /api/alerts?camera_id=CAM_01&limit=100
```

### Get Persons
```
GET /api/persons
```

### Get Statistics
```
GET /api/stats
```

## Pages Available

1. **Main Page**: `http://localhost:8000/`
   - Video feed and analytics

2. **Database Viewer**: `http://localhost:8000/database`
   - View alerts and persons
   - Statistics dashboard
   - Filtering and search

## Usage

1. Run the pipeline to generate alerts
2. Open the database viewer in your browser
3. View real-time statistics and alerts
4. Filter by type or camera as needed
5. Check registered persons

## Example Workflow

```bash
# Terminal 1: Run the pipeline
python run_pipeline.py --source "sample.mp4" --camera-id CAM_01

# Terminal 2: Start web server
uvicorn app.app:app --reload

# Browser: Open database viewer
http://localhost:8000/database
```

Enjoy your database viewer! 🎉
