import os
from config import logger

# Lazy load faster-whisper to keep initial startup fast
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            # Run on CPU with int8 quantization to save VRAM and keep it lightweight
            logger.info("Loading CPU-bound Faster-Whisper model (base.en)...")
            _whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
        except Exception as e:
            logger.error(f"Failed to load Faster-Whisper: {e}")
            return None
    return _whisper_model

def transcribe_audio_file(audio_filepath):
    """
    Transcribes a local audio file (.ogg, .mp3, .wav) using CPU Faster-Whisper.
    Returns transcript text string.
    """
    model = get_whisper_model()
    if not model:
        return "[Error: Faster-Whisper model not loaded]"
        
    try:
        segments, info = model.transcribe(audio_filepath, beam_size=5)
        transcript = " ".join([segment.text for segment in segments]).strip()
        logger.info(f"Transcribed audio ({info.duration:.2f}s): {transcript}")
        return transcript
    except Exception as e:
        logger.error(f"Error during audio transcription: {e}")
        return f"[Error transcribing audio: {e}]"
