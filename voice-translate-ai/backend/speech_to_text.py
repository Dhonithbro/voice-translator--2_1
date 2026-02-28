"""
=============================================================
  SPEECH-TO-TEXT MODULE — Real-Time Voice Translator
  Uses SpeechRecognition with Google Web Speech API (free tier)
  as primary engine; whisper as optional offline engine.
=============================================================
"""

import os, time, tempfile

# ── SpeechRecognition ─────────────────────────────────────────────────────────
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

# ── Optional: OpenAI Whisper (local, fully offline) ──────────────────────────
try:
    import whisper as whisper_lib
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class SpeechToText:
    """
    Converts microphone audio or audio bytes to text.

    Engines (in priority order):
      1. 'whisper' — local OpenAI Whisper (no internet required)
      2. 'google'  — Google Web Speech API (requires internet)
      3. 'sphinx'  — PocketSphinx (local, lower accuracy)
    """

    def __init__(self, engine: str = "google", whisper_model: str = "base"):
        self.engine        = engine
        self.recognizer    = sr.Recognizer() if SR_AVAILABLE else None
        self.whisper_model = None

        if engine == "whisper" and WHISPER_AVAILABLE:
            print(f"[~] Loading Whisper model '{whisper_model}'...")
            self.whisper_model = whisper_lib.load_model(whisper_model)
            print("[✓] Whisper ready.")

        # Adjust for ambient noise sensitivity
        if self.recognizer:
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8  # seconds of silence before stopping

    # ── Microphone capture ────────────────────────────────────────────────────
    def listen_from_microphone(self, timeout: int = 5, phrase_time_limit: int = 15) -> dict:
        """
        Capture audio from default microphone and transcribe.

        timeout          — seconds to wait for speech to begin
        phrase_time_limit — maximum seconds of audio to capture
        """
        if not SR_AVAILABLE:
            return {"error": "speech_recognition not installed", "text": ""}

        with sr.Microphone() as source:
            print("[~] Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[●] Listening...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
            except sr.WaitTimeoutError:
                return {"error": "No speech detected within timeout", "text": ""}

        return self._transcribe(audio)

    # ── Transcribe from audio bytes (for WebSocket/API use) ──────────────────
    def transcribe_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> dict:
        """Transcribe raw PCM audio bytes."""
        if not SR_AVAILABLE:
            return {"error": "speech_recognition not installed", "text": ""}
        audio = sr.AudioData(audio_bytes, sample_rate, 2)
        return self._transcribe(audio)

    # ── Core transcription ────────────────────────────────────────────────────
    def _transcribe(self, audio) -> dict:
        t0 = time.perf_counter()
        try:
            if self.engine == "whisper" and self.whisper_model:
                # Save audio to temp file and run Whisper
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio.get_wav_data())
                    tmp_path = tmp.name
                result = self.whisper_model.transcribe(tmp_path, language="en")
                os.unlink(tmp_path)
                text = result["text"].strip()

            elif self.engine == "google":
                text = self.recognizer.recognize_google(audio, language="en-US")

            elif self.engine == "sphinx":
                text = self.recognizer.recognize_sphinx(audio)

            else:
                text = self.recognizer.recognize_google(audio, language="en-US")

            latency = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "text":       text,
                "engine":     self.engine,
                "latency_ms": latency,
                "error":      None,
            }

        except sr.UnknownValueError:
            return {"error": "Could not understand audio", "text": "", "engine": self.engine}
        except sr.RequestError as e:
            return {"error": f"API unavailable: {e}", "text": "", "engine": self.engine}
        except Exception as e:
            return {"error": str(e), "text": "", "engine": self.engine}


# ── Singleton instance ────────────────────────────────────────────────────────
_stt_instance: SpeechToText | None = None


def get_stt(engine: str = "google") -> SpeechToText:
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = SpeechToText(engine=engine)
    return _stt_instance


def transcribe_audio_bytes(audio_bytes: bytes, sample_rate: int = 16000) -> dict:
    """Convenience wrapper used by the FastAPI backend."""
    return get_stt().transcribe_bytes(audio_bytes, sample_rate)
