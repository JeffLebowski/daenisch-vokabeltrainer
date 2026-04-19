"""
Dänisch Vokabel-Audio-Generator
================================
Voraussetzungen:
    pip install gtts pydub

Außerdem wird ffmpeg benötigt:
    - Windows: https://ffmpeg.org/download.html  (ffmpeg.exe in PATH oder ins Skript-Verzeichnis)
    - Mac:     brew install ffmpeg
    - Linux:   sudo apt install ffmpeg

Verwendung:
    python create_audio.py

Ausgabe:
    daenisch_lektion14_15.mp3

Aufbau jedes Eintrags:
    Substantive:  deutsches Wort → Singular, bestimmter Singular, Plural, bestimmter Plural
    Verben:       deutsches Wort → Grundform, Präsens, Präteritum, Perfekt
    Sonstige:     deutsches Wort → dänisches Wort (normal + langsam)
"""

import json
import os
import sys
import tempfile

try:
    from gtts import gTTS
except ImportError:
    sys.exit("Fehler: gtts nicht installiert. Bitte 'pip install gtts' ausführen.")

try:
    from pydub import AudioSegment
except ImportError:
    sys.exit("Fehler: pydub nicht installiert. Bitte 'pip install pydub' ausführen.")

# ── Konfiguration ──────────────────────────────────────────────────────────────

VOKABELN_FILE = "vokabeln.json"
OUTPUT_FILE   = "daenisch_lektion14_15.mp3"

PAUSE_KURZ    = 700   # ms – zwischen Formen
PAUSE_MITTEL  = 1100  # ms – nach deutschem Wort
PAUSE_LANG    = 1900  # ms – nach jedem Vokabel-Block

# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def tts(text: str, lang: str, slow: bool = False) -> AudioSegment:
    """Synthetisiert Text mit gTTS und gibt ein AudioSegment zurück."""
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    try:
        gTTS(text=text, lang=lang, slow=slow).save(tmp.name)
        seg = AudioSegment.from_mp3(tmp.name)
    finally:
        os.unlink(tmp.name)
    return seg

def stille(ms: int) -> AudioSegment:
    return AudioSegment.silent(duration=ms)

# ── Hauptprogramm ──────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(VOKABELN_FILE):
        sys.exit(f"Fehler: '{VOKABELN_FILE}' nicht gefunden. "
                 "Bitte beide Dateien im selben Ordner ablegen.")

    with open(VOKABELN_FILE, encoding="utf-8") as f:
        alle = json.load(f)

    # Nur echte Einträge (keine Kommentarzeilen)
    vokabeln = [e for e in alle if e.get("de") and e.get("da")]

    print(f"Starte Audio-Generierung: {len(vokabeln)} Vokabeln ...")
    print("(Das kann je nach Internetverbindung einige Minuten dauern.)\n")

    audio = stille(500)

    # Intro
    audio += tts("Dänisch Vokabeltraining. Lektion vierzehn und fünfzehn.", "de")
    audio += stille(PAUSE_LANG)

    for i, eintrag in enumerate(vokabeln, 1):
        de     = eintrag["de"]
        da     = eintrag["da"]
        typ    = eintrag.get("typ", "sonstig")
        formen = eintrag.get("formen") or []

        print(f"[{i:3}/{len(vokabeln)}]  {de}  ->  {da}  ({typ})")

        # 1. Deutsches Wort
        audio += tts(de, "de")
        audio += stille(PAUSE_MITTEL)

        if typ in ("substantiv", "verb") and formen:
            # Direkt alle Formen nacheinander – kein separates Grundwort davor
            for form in formen:
                audio += tts(form, "da")
                audio += stille(PAUSE_KURZ)
        else:
            # Adjektive, Adverbien, feste Ausdrücke: dänisches Wort normal + langsam
            audio += tts(da, "da")
            audio += stille(PAUSE_KURZ)
            audio += tts(da, "da", slow=True)
            audio += stille(PAUSE_KURZ)

        audio += stille(PAUSE_LANG)

    # Export
    print(f"\nSpeichere '{OUTPUT_FILE}' ...")
    audio.export(OUTPUT_FILE, format="mp3", bitrate="128k")

    dauer = len(audio) / 1000
    print(f"Fertig! Dauer: {dauer:.0f} s ({dauer / 60:.1f} min)")
    print(f"Datei:  {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    main()
