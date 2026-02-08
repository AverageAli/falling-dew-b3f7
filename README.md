# KurdSmart (Windows Desktop App)

KurdSmart is a **Windows-only**, offline-first Kurdish language learning desktop application built with **Python 3.11+**, **PySide6**, and **SQLite**.

It is designed for serious learners who need a fast assistant for:
- Dictionary lookup (Kurdish ↔ Persian ↔ English)
- Domain-specific vocabulary (general, medical, technical)
- Sentence generation and sentence analysis
- Pronunciation (text-to-speech) with adjustable speed
- Dialect awareness (Sorani, Kurmanji)
- Interactive exercises
- Saved vocabulary review

## Project Layout

```text
kurdsmart/
  app.py                         # Entry point
  requirements.txt
  kurdsmart/
    __init__.py
    main_window.py               # PySide6 GUI and UI flow
    database.py                  # SQLite schema + seed data
    workers.py                   # Generic QThread worker utility
    services/
      dictionary_service.py
      sentence_service.py
      practice_service.py
      tts_service.py
```

## Quick Start (Development)

1. Create a Python 3.11+ environment on Windows.
2. Install dependencies:

```bash
pip install -r kurdsmart/requirements.txt
```

3. Run the app:

```bash
python kurdsmart/app.py
```

The app creates a local SQLite database automatically at:

```text
%USERPROFILE%\AppData\Local\KurdSmart\kurdsmart.db
```

## Design Notes

- **No UI freezing:** TTS operations run in background threads using `QThread` worker pattern.
- **Offline-first:** core dictionary/exercises are bundled as SQLite seed data.
- **Expandable dialect/content model:** dialect and domain fields are explicit in schema.
- **Tutor-like UX:** focused tabs (Dictionary, Sentences, Practice, Saved Vocabulary), simple controls, and immediate feedback.

## Build Windows `.exe` with PyInstaller

Install PyInstaller:

```bash
pip install pyinstaller
```

Create one-folder executable:

```bash
pyinstaller --noconfirm --windowed --name KurdSmart --paths kurdsmart kurdsmart/app.py
```

Output will be in:

```text
dist/KurdSmart/
```

Create one-file executable (optional):

```bash
pyinstaller --noconfirm --windowed --onefile --name KurdSmart --paths kurdsmart kurdsmart/app.py
```

## Notes for Pronunciation

- TTS is implemented via `pyttsx3` (offline engine, suitable for Windows/SAPI voices).
- If TTS backend is unavailable, the app reports a clear message and continues functioning.

## Future Production Extensions

- More comprehensive lexical database import pipeline
- Spaced repetition scheduling for saved words
- Audio caching
- Rich grammar diagnostics and error explanation engine
- Additional dialect packs and custom lessons
