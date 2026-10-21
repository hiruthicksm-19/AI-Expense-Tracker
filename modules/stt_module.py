"""
Speech-to-Text (STT) module using OpenAI Whisper.

Provides functionality to transcribe audio to text.
"""

import os
import tempfile
import streamlit as st
import whisper


@st.cache_resource
def load_whisper_model():
    """
    Load the local English-only Whisper model once.
    
    Uses cache to avoid reloading the model on every call.
    
    Returns:
        whisper.Whisper: The loaded Whisper model
    """
    return whisper.load_model("tiny.en", device="cpu")


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe WAV audio bytes into English text.
    
    Args:
        audio_bytes: Audio data in bytes (WAV format)
        
    Returns:
        str: Transcribed text
        
    Raises:
        ValueError: If no audio provided or no speech recognized
    """
    if not audio_bytes:
        raise ValueError("No audio was provided.")
    
    model = load_whisper_model()
    temp_path = None
    
    try:
        # Write audio bytes to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        # Transcribe using Whisper
        result = model.transcribe(
            temp_path,
            language="en",
            task="transcribe",
            fp16=False,
        )
        
        # Extract and validate text
        text = result["text"].strip()
        
        if not text:
            raise ValueError("No speech was recognized. Please try again.")
        
        return text
    
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
