# Speech-to-Text (STT) Integration Guide

## Overview

The Invoice Expense Tracker now includes a **Speech-to-Text (STT)** feature that allows you to ask questions about your expenses using voice input.

## Features

✓ **Microphone Recording** - Click the microphone icon to record your question
✓ **Real-time Transcription** - Audio is automatically transcribed to text using OpenAI Whisper
✓ **Auto-fill Text Input** - Transcribed text automatically appears in the chatbox
✓ **Natural Language Queries** - Ask questions like "What is my total spending?" using your voice
✓ **LLM Processing** - Transcribed questions are processed by LLM to generate MongoDB queries

## How to Use

### 1. Access the Query Assistant
- Scroll to the "Query Assistant - Ask Questions About Your Expenses" section
- You'll see:
  - A text input field (for manual queries)
  - A "Search" button
  - A voice input section with microphone icon

### 2. Recording Audio
- Click the microphone icon (🎤) in the "Voice Input" section
- Your browser will request microphone permission (grant access)
- Speak your question clearly
- The recording will start automatically

### 3. Stopping the Recording
- Click the "Stop" button to finish recording
- Wait for the transcription to complete (you'll see a spinner)

### 4. Review & Submit
- The transcribed text will appear in the text input field
- Review the transcription for accuracy
- Click "Search" to process your question with LLM

### 5. View Results
- The LLM will generate a MongoDB query
- Results will display as a natural language answer
- Expand "Query Details" to see the generated pipeline and raw results

## Example Workflows

### Example 1: Total Spending
1. Click microphone
2. Say: "What is my total spending?"
3. Transcription appears: "What is my total spending?"
4. Click "Search"
5. Answer: "Your total spending is ₹649,681.08..."

### Example 2: Monthly Breakdown
1. Click microphone
2. Say: "Show me invoices from May 2026"
3. Transcription appears: "Show me invoices from May 2026"
4. Click "Search"
5. Answer: "Found 2 invoices from May 2026..."

## Technical Details

### STT Module (`modules/stt_module.py`)

**Functions:**
- `load_whisper_model()` - Loads the Whisper model once (cached)
- `transcribe_audio(audio_bytes)` - Converts WAV audio bytes to text

**Model:** `tiny.en` - English-only, optimized for CPU
**Language:** English
**Device:** CPU (no GPU required)

### Supported Audio Formats
- WAV format (primary)
- MP3, FLAC (browser-dependent)
- Mono or stereo
- 16kHz or higher sample rate recommended

### Browser Requirements
- Modern browser with microphone support
- Chrome, Firefox, Safari, Edge (all recent versions)
- HTTPS connection (required for microphone access)

### Error Handling

| Error | Solution |
|-------|----------|
| "No microphone found" | Check browser permissions, connect a microphone |
| "No speech recognized" | Speak louder, reduce background noise |
| "Transcription failed" | Check internet connection, try again |
| "AudioContext error" | Refresh the page, check browser console |

## Session State Management

- Transcribed text is stored in `st.session_state.transcribed_text`
- Text persists until "Search" is clicked
- Session clears after successful query submission

## Performance Notes

⚠️ **First Time Use:**
- Whisper model (~140MB) downloads on first use
- May take 30-60 seconds to load
- Subsequent uses are faster (model cached)

**Transcription Speed:**
- 30-second audio: ~5-10 seconds
- 60-second audio: ~10-15 seconds
- Depends on system CPU

## Limitations

- English language only (model: `tiny.en`)
- Audio must be clear and intelligible
- Works best in quiet environments
- Maximum audio length: browser-dependent (typically 10-15 minutes)

## Troubleshooting

### Microphone Not Working
```
1. Check browser microphone permissions
2. Refresh the page
3. Try a different browser
4. Check if microphone is connected and working
```

### Transcription Quality Issues
```
1. Reduce background noise
2. Speak clearly and slowly
3. Use a better microphone
4. Use text input instead for complex queries
```

### Model Not Loading
```
1. Check internet connection
2. Check disk space (~200MB free)
3. Restart Streamlit app
4. Check console for error details
```

## Future Enhancements

- [ ] Multi-language support
- [ ] Speaker identification
- [ ] Audio waveform visualization
- [ ] Voice command shortcuts
- [ ] Transcript history/logging
- [ ] Custom wake words

## Files Modified

- `app.py` - Added STT UI in Query Assistant section
- `modules/stt_module.py` - New STT module
- `modules/__init__.py` - Added STT module exports
- `requirements.txt` - Added `openai-whisper`

## References

- OpenAI Whisper: https://github.com/openai/whisper
- Streamlit Audio Input: https://docs.streamlit.io/library/api-reference/widgets/st.audio_input
- Streamlit Audio Component: https://docs.streamlit.io/library/api-reference/media/st.audio
