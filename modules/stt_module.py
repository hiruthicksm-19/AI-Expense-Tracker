"""Local Whisper speech-to-text support for the query assistant.

This module deliberately keeps recorded audio on the user's machine. The
audio is written to a temporary file, transcribed by the local Whisper model,
and deleted immediately after transcription.
"""

import os
import tempfile

import streamlit as st
import whisper


WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "base.en")


@st.cache_resource
def load_whisper_model():
    """Load and cache the configured local Whisper model."""
    return whisper.load_model(WHISPER_MODEL_NAME)


def transcribe_audio(audio_bytes: bytes, suffix: str = ".wav") -> str:
    """Transcribe recorded audio locally with Whisper.

    Args:
        audio_bytes: Bytes returned by Streamlit's ``st.audio_input``.
        suffix: Temporary-file suffix matching the recording format.

    Returns:
        Trimmed English transcription.

    Raises:
        ValueError: If audio is empty or no speech is recognized.
        Exception: If Whisper cannot process the recording.
    """
    if not audio_bytes:
        raise ValueError("No audio was recorded.")

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as audio_file:
            audio_file.write(audio_bytes)
            temporary_path = audio_file.name

        result = load_whisper_model().transcribe(
            temporary_path,
            language="en",
            task="transcribe",
            fp16=False,
            temperature=0.0,
        )

        text = result.get("text", "").strip()
        if not text:
            raise ValueError("No speech was recognized. Please try recording again.")

        return text
    except ValueError:
        raise
    except Exception as error:
        raise Exception(f"Error transcribing audio with Whisper: {error}") from error
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)
