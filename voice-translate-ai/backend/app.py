"""
FastAPI Backend — Bidirectional Voice Translator
Source : English | Hindi | Telugu | Tamil | Malayalam
Target : English | Hindi | Telugu | Tamil | Malayalam | German | French | Spanish
"""
import os, sys, json, time, base64, asyncio
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from translator     import translate, supported_languages
from text_to_speech import synthesize
from speech_to_text import transcribe_audio_bytes

app = FastAPI(
    title       = "Bidirectional Voice Translator",
    description = "Translate between English, Hindi, Telugu, Tamil, Malayalam, German, French, Spanish",
    version     = "2.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class TranslateRequest(BaseModel):
    text:     str
    src_lang: str = "english"
    tgt_lang: str = "telugu"
    tts:      bool = True

class AudioRequest(BaseModel):
    audio_b64:   str
    src_lang:    str = "english"
    tgt_lang:    str = "telugu"
    sample_rate: int = 16000

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}

@app.get("/languages")
async def get_languages():
    return supported_languages()

@app.post("/translate")
async def translate_text(req: TranslateRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(400, "text cannot be empty")
    
    # Validate language codes
    from translator import LANGUAGES
    src_lower = req.src_lang.lower()
    # allow automatic detection
    if src_lower not in LANGUAGES and src_lower not in ("auto", "detect"):
        raise HTTPException(400, f"Source language '{req.src_lang}' not supported")
    if req.tgt_lang.lower() not in LANGUAGES:
        raise HTTPException(400, f"Target language '{req.tgt_lang}' not supported")
    
    t0 = time.perf_counter()
    tr = await asyncio.to_thread(translate, req.text, req.src_lang, req.tgt_lang)
    
    # Check if translation was successful
    if tr.get("source") == "error":
        raise HTTPException(500, tr.get("translated", "Translation failed"))
    
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
    
    # Add audio if requested and translation is valid
    if req.tts and tr.get("translated") and not tr["translated"].startswith("❌") and not tr["translated"].startswith("⚠️"):
        tts = await asyncio.to_thread(synthesize, tr["translated"], req.tgt_lang)
        if tts.get("audio_b64"):
            result["audio_b64"]  = tts.get("audio_b64")
            result["audio_mime"] = tts.get("mime_type", "audio/mpeg")
            result["tts_ms"]     = tts.get("latency_ms", 0)
    
    result["total_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return JSONResponse(content=result)

@app.post("/translate-audio")
async def translate_audio(req: AudioRequest):
    t0 = time.perf_counter()
    try:
        audio_bytes = base64.b64decode(req.audio_b64)
    except Exception:
        raise HTTPException(400, "Invalid base64 audio")
    stt = await asyncio.to_thread(transcribe_audio_bytes, audio_bytes, req.sample_rate)
    if stt.get("error") or not stt.get("text"):
        return JSONResponse({"error": stt.get("error", "STT failed"), "text": ""})
    tr  = await asyncio.to_thread(translate, stt["text"], req.src_lang, req.tgt_lang)
    tts = await asyncio.to_thread(synthesize, tr.get("translated", ""), req.tgt_lang)
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
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON payload"})
                continue
                
            text     = payload.get("text", "").strip()
            src_lang = payload.get("src_lang", "english")
            tgt_lang = payload.get("tgt_lang", "telugu")
            if not text:
                await websocket.send_json({"error": "Empty text"})
                continue
            tr  = await asyncio.to_thread(translate, text, src_lang, tgt_lang)
            tts = await asyncio.to_thread(synthesize, tr.get("translated", ""), tgt_lang)
            await websocket.send_json({
                "original":   text,
                "translated": tr.get("translated"),
                "confidence": tr.get("confidence"),
                "latency_ms": tr.get("latency_ms"),
                "source":     tr.get("source"),
                "src_lang":   src_lang,
                "tgt_lang":   tgt_lang,
                "audio_b64":  tts.get("audio_b64"),
                "audio_mime": tts.get("mime_type", "audio/mpeg"),
            })
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
