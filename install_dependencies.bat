@echo off
echo Installing all required dependencies...
echo.

pip install shapely==2.0.3
pip install deep-sort-realtime
pip install transformers
pip install facenet-pytorch
pip install ultralytics
pip install opencv-python
pip install numpy
pip install Pillow
pip install fastapi
pip install uvicorn

echo.
echo All dependencies installed!
pause
