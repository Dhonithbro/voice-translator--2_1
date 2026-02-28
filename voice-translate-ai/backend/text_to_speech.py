"""
=============================================================
  TEXT-TO-SPEECH MODULE — Real-Time Voice Translator
  Uses gTTS (Google Text-to-Speech) for audio synthesis
  Encodes output as base64 for streaming to browser
=============================================================
"""

import os, time, base64, tempfile, io

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


# ── Language code mapping for gTTS ───────────────────────────────────────────
GTTS_LANG_MAP = {
    "hindi":   "hi",
    "telugu":  "te",
    "tamil":   "ta",
    "malayalam": "ml",
    "german":  "de",
    "french":  "fr",
    "spanish": "es",
    "english": "en",
}


def synthesize(text: str, language: str = "french") -> dict:
    """
    Convert `text` to speech for the given language.

    Returns:
      audio_b64  : base64-encoded MP3 bytes (play directly in browser)
      latency_ms : float
      engine     : str
    """
    t0 = time.perf_counter()
    lang_code = GTTS_LANG_MAP.get(language.lower(), "fr")

    # ── gTTS (online) ─────────────────────────────────────────────────────────
    if GTTS_AVAILABLE:
        try:
            tts = gTTS(text=text, lang=lang_code, slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            audio_bytes = buf.read()
            latency     = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "audio_b64":  base64.b64encode(audio_bytes).decode("utf-8"),
                "mime_type":  "audio/mpeg",
                "latency_ms": latency,
                "engine":     "gTTS",
                "error":      None,
            }
        except Exception as e:
            print(f"[!] gTTS failed: {e}")

    # ── pyttsx3 (offline fallback) ────────────────────────────────────────────
    if PYTTSX3_AVAILABLE:
        try:
            engine = pyttsx3.init()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()
            os.unlink(tmp_path)
            latency = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "audio_b64":  base64.b64encode(audio_bytes).decode("utf-8"),
                "mime_type":  "audio/wav",
                "latency_ms": latency,
                "engine":     "pyttsx3",
                "error":      None,
            }
        except Exception as e:
            print(f"[!] pyttsx3 failed: {e}")

    return {
        "audio_b64":  None,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
        "engine":     "none",
        "error":      "No TTS engine available. Install: pip install gtts",
    }


def synthesize_to_file(text: str, language: str, output_path: str) -> bool:
    """Synthesize and save audio to a file. Returns True on success."""
    result = synthesize(text, language)
    if result.get("audio_b64"):
        audio_bytes = base64.b64decode(result["audio_b64"])
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return True
    return False
