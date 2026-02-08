from __future__ import annotations


class TTSService:
    def __init__(self) -> None:
        self._engine = None
        self._import_error = None
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
        except Exception as exc:  # graceful fallback if TTS backend unavailable
            self._import_error = exc

    def speak(self, text: str, rate: int) -> str:
        if not text.strip():
            return "No text provided for pronunciation."

        if self._engine is None:
            return (
                "TTS engine unavailable. Install pyttsx3 on Windows for offline pronunciation. "
                f"Details: {self._import_error}"
            )

        self._engine.setProperty("rate", rate)
        self._engine.say(text)
        self._engine.runAndWait()
        return "Pronunciation finished."
