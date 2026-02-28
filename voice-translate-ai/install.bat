@echo off
echo ================================================
echo   VoiceTranslate AI - Installing Dependencies
echo ================================================
echo.

echo [1/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/4] Installing Google Translate (deep-translator)...
pip install deep-translator

echo.
echo [3/4] Installing FastAPI + Speech packages...
pip install fastapi "uvicorn[standard]" pydantic python-multipart websockets
pip install SpeechRecognition gTTS pyttsx3

echo.
echo [4/4] Installing utilities...
pip install numpy tqdm python-dotenv

echo.
echo ================================================
echo   ALL DONE!
echo   Now run:  python backend/app.py
echo   Then open frontend/index.html in Chrome
echo ================================================
pause
