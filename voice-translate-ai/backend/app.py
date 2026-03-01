"""
FastAPI Backend — Bidirectional Voice Translator
Compatible with Python 3.13 + pydantic v2
"""
import os, sys, json, time, base64
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from translator     import translate, supported_languages
from text_to_speech import synthesize
from speech_to_text import transcribe_audio_bytes

app = FastAPI(
    title       = "Bidirectional Voice Translator",
    description = "Translate between English, Hindi, Telugu, Tamil, Malayalam, German, French, Spanish",
    version     = "3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslateRequest(BaseModel):
    text:     str
    src_lang: str = "english"
    tgt_lang: str = "telugu"
    tts:      bool = True

class DetectRequest(BaseModel):
    text: str

class AudioRequest(BaseModel):
    audio_b64:   str
    src_lang:    str = "english"
    tgt_lang:    str = "telugu"
    sample_rate: int = 16000

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}

@app.post("/detect")
async def detect_language(req: DetectRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "text is empty")
    try:
        from deep_translator import GoogleTranslator
        # Use translate to detect: translate to English and get source
        from deep_translator.exceptions import LanguageNotSupportedException
        import unicodedata
        # Script-based detection first (fast, offline)
        counts = {"telugu":0,"hindi":0,"tamil":0,"malayalam":0}
        for ch in text:
            cp = ord(ch)
            if 0x0C00 <= cp <= 0x0C7F: counts["telugu"] += 1
            elif 0x0900 <= cp <= 0x097F: counts["hindi"] += 1
            elif 0x0B80 <= cp <= 0x0BFF: counts["tamil"] += 1
            elif 0x0D00 <= cp <= 0x0D7F: counts["malayalam"] += 1
        mx = max(counts.values())
        if mx > 0:
            lang = max(counts, key=counts.get)
            labels = {"telugu":"Telugu","hindi":"Hindi","tamil":"Tamil","malayalam":"Malayalam"}
            return {"language": lang, "language_name": labels[lang], "confidence": 0.99}
        # Default to English for Latin script
        return {"language": "english", "language_name": "English", "confidence": 0.90}
    except Exception as e:
        return {"language": "english", "language_name": "English", "confidence": 0.5}

@app.get("/languages")
async def get_languages():
    return supported_languages()

@app.post("/translate")
async def translate_text(req: TranslateRequest):
    if not req.text.strip():
        raise HTTPException(400, "text cannot be empty")
    t0 = time.perf_counter()
    tr = translate(req.text, req.src_lang, req.tgt_lang)
    if "error" in tr:
        raise HTTPException(500, tr["error"])
    result = {
        "original":     tr["original"],
        "translated":   tr["translated"],
        "src_lang":     tr["src_lang"],
        "tgt_lang":     tr["tgt_lang"],
        "model":        tr["model_used"],
        "source":       tr["source"],
        "confidence":   tr["confidence"],
        "translate_ms": tr["latency_ms"],
    }
    if req.tts and tr.get("translated") and not tr["translated"].startswith("⚠"):
        try:
            tts = synthesize(tr["translated"], req.tgt_lang)
            result["audio_b64"]  = tts.get("audio_b64")
            result["audio_mime"] = tts.get("mime_type", "audio/mpeg")
            result["tts_ms"]     = tts.get("latency_ms", 0)
        except Exception:
            pass
    result["total_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return JSONResponse(content=result)

@app.post("/translate-audio")
async def translate_audio(req: AudioRequest):
    t0 = time.perf_counter()
    try:
        audio_bytes = base64.b64decode(req.audio_b64)
    except Exception:
        raise HTTPException(400, "Invalid base64 audio")
    stt = transcribe_audio_bytes(audio_bytes, req.sample_rate)
    if stt.get("error") or not stt.get("text"):
        return JSONResponse({"error": stt.get("error", "STT failed"), "text": ""})
    tr  = translate(stt["text"], req.src_lang, req.tgt_lang)
    tts = {}
    try:
        tts = synthesize(tr.get("translated", ""), req.tgt_lang)
    except Exception:
        pass
    return JSONResponse({
        "spoken_text":  stt["text"],
        "translated":   tr.get("translated"),
        "src_lang":     req.src_lang,
        "tgt_lang":     req.tgt_lang,
        "confidence":   tr.get("confidence"),
        "audio_b64":    tts.get("audio_b64"),
        "audio_mime":   tts.get("mime_type", "audio/mpeg"),
        "total_ms":     round((time.perf_counter()-t0)*1000, 2),
    })

@app.websocket("/ws/translate")
async def ws_translate(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data    = await websocket.receive_text()
            payload = json.loads(data)
            text     = payload.get("text", "").strip()
            src_lang = payload.get("src_lang", "english")
            tgt_lang = payload.get("tgt_lang", "telugu")
            if not text:
                await websocket.send_json({"error": "Empty text"})
                continue
            tr = translate(text, src_lang, tgt_lang)
            tts = {}
            try:
                tts = synthesize(tr.get("translated", ""), tgt_lang)
            except Exception:
                pass
            await websocket.send_json({
                "original":   text,
                "translated": tr.get("translated"),
                "confidence": tr.get("confidence"),
                "latency_ms": tr.get("latency_ms"),
                "audio_b64":  tts.get("audio_b64"),
            })
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=False)
