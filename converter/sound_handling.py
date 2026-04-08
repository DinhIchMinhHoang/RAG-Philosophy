"""
Audio converters: STT (speech-to-text) for mp3, wav, m4a, flac, ogg.
"""
import logging
from pathlib import Path
from typing import Optional

from .base import BaseConverter
from .types import ConvertedContent, ConversionMetadata

try:
    import whisper
except ImportError:
    whisper = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


logger = logging.getLogger(__name__)


class WhisperSTTBase:
    """Base class for Whisper STT engines."""

    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac"}

    def __init__(self, model_size: str = "small", language: str = "vi", use_gpu: bool = False):
        """
        Initialize Whisper STT.
        Args:
            model_size: "tiny", "base", "small", "medium", "large"
            language: Language code (e.g., 'vi' for Vietnamese)
            use_gpu: Use GPU if available (default: False)
        """
        self.model_size = model_size
        self.language = language
        self.use_gpu = use_gpu
        self.model = None
        self._init_model()

    def _init_model(self):
        """Initialize the model (to be implemented by subclasses)."""
        raise NotImplementedError

    def transcribe(self, audio_path: str) -> tuple[str, Optional[float]]:
        """Transcribe audio file. Returns (transcript, duration)."""
        raise NotImplementedError


class OpenAIWhisperSTT(WhisperSTTBase):
    """STT using OpenAI Whisper."""

    def _init_model(self):
        if not whisper:
            raise RuntimeError(
                "openai-whisper not installed (install: pip install openai-whisper)"
            )
        try:
            self.model = whisper.load_model(self.model_size)
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe(self, audio_path: str) -> tuple[str, Optional[float]]:
        if not self.model:
            raise RuntimeError("Whisper model not initialized")
        try:
            result = self.model.transcribe(audio_path, language=self.language)
            transcript = result.get("text", "")
            duration = None  # Whisper doesn't directly provide duration
            return transcript, duration
        except Exception as e:
            logger.error(f"Whisper transcription failed for {audio_path}: {e}")
            raise


class FasterWhisperSTT(WhisperSTTBase):
    """STT using faster-whisper (faster, more efficient)."""

    def _init_model(self):
        if not WhisperModel:
            raise RuntimeError(
                "faster-whisper not installed (install: pip install faster-whisper)"
            )
        try:
            # Use GPU if enabled, otherwise use CPU
            device = "cuda" if self.use_gpu else "cpu"
            compute_type = "float16" if self.use_gpu else "float32"
            self.model = WhisperModel(self.model_size, device=device, compute_type=compute_type)
        except Exception as e:
            logger.error(f"Failed to load faster-whisper model: {e}")
            raise

    def transcribe(self, audio_path: str) -> tuple[str, Optional[float]]:
        if not self.model:
            raise RuntimeError("Whisper model not initialized")
        try:
            segments, info = self.model.transcribe(
                audio_path, language=self.language, beam_size=5
            )
            texts = [segment.text for segment in segments]
            transcript = " ".join(texts)
            duration = info.duration if info else None
            return transcript, duration
        except Exception as e:
            logger.error(f"faster-whisper transcription failed for {audio_path}: {e}")
            raise


class AudioConverter(BaseConverter):
    """Convert audio files (mp3, wav, m4a, etc.) to text via STT."""

    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac", ".m4b"}

    def __init__(
        self,
        use_faster_whisper: bool = True,
        model_size: str = "small",
        language: str = "vi",
        use_gpu: bool = False,
    ):
        """
        Initialize audio converter.
        Args:
            use_faster_whisper: Use faster-whisper if True, else openai-whisper
            model_size: Model size ("tiny", "base", "small", "medium", "large")
            language: Language code (e.g., 'vi' for Vietnamese)
            use_gpu: Use GPU if available (default: False)
        """
        self.use_faster_whisper = use_faster_whisper
        self.model_size = model_size
        self.language = language
        self.use_gpu = use_gpu
        self.stt_engine = None
        self._init_stt_engine()

    def _init_stt_engine(self):
        """Initialize STT engine."""
        try:
            if self.use_faster_whisper and WhisperModel:
                self.stt_engine = FasterWhisperSTT(
                    model_size=self.model_size, language=self.language, use_gpu=self.use_gpu
                )
                logger.info(f"Initialized faster-whisper STT engine (GPU: {self.use_gpu})")
            elif whisper:
                self.stt_engine = OpenAIWhisperSTT(
                    model_size=self.model_size, language=self.language, use_gpu=self.use_gpu
                )
                logger.info("Initialized OpenAI Whisper STT engine")
            else:
                logger.warning(
                    "No Whisper implementation available (install faster-whisper or openai-whisper)"
                )
        except Exception as e:
            logger.error(f"Failed to initialize STT engine: {e}")

    def can_handle(self, file_path: str) -> bool:
        ext = Path(file_path).suffix.lower()
        return ext in self.AUDIO_EXTENSIONS

    def convert(self, file_path: str) -> ConvertedContent:
        if not self.stt_engine:
            return ConvertedContent(
                text="",
                metadata=self.create_metadata(
                    file_path, "audio", "stt", language=self.language
                ),
                success=False,
                error="STT engine not initialized",
            )

        try:
            transcript, duration = self.stt_engine.transcribe(file_path)
            text = self.normalize_text(transcript)

            metadata = self.create_metadata(
                file_path,
                Path(file_path).suffix.lstrip("."),
                "stt",
                language=self.language,
                duration=duration,
                model_size=self.model_size,
                stt_engine="faster-whisper"
                if isinstance(self.stt_engine, FasterWhisperSTT)
                else "openai-whisper",
            )
            return ConvertedContent(text=text, metadata=metadata, success=True)
        except Exception as e:
            logger.error(f"Error converting audio {file_path}: {e}")
            return ConvertedContent(
                text="",
                metadata=self.create_metadata(
                    file_path, "audio", "stt", language=self.language
                ),
                success=False,
                error=str(e),
            )
