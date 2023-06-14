import os
import io
import logging

from torch import cuda

from tts_worker.config import ModelConfig
from tts_worker.schemas import Request, Response, ResponseContent
from tts_worker.utils import clean



from TTS.config import load_config
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer as SynthesizerTTS

logger = logging.getLogger(__name__)

SPEAKER_PREFIX = os.getenv('SPEAKER_PREFIX', 'vits_')

class Synthesizer:
    def __init__(self, model_config: ModelConfig):
        self.model_name = model_config.model_name
        
        model_path = os.path.join(model_config.model_path, 'model.pth')
        config_path = os.path.join(model_config.model_path, 'config.json')
        speakers_path = os.path.join(model_config.model_path, 'speakers.pth')
        self.model = SynthesizerTTS(
            tts_checkpoint=model_path,
            tts_config_path=config_path,
            tts_speakers_file=speakers_path,
            use_cuda=cuda.is_available(),
        )

        model_speakers = self.model.tts_model.speaker_manager.speaker_names
        self.speakers = [SPEAKER_PREFIX + speaker for speaker in model_speakers]
        
        self.sampling_rate = self.model.tts_config.audio.sample_rate


    def process_request(self, request: Request) -> Response:
        logger.info(f"Request received: {{"
                    f"speaker: {request.speaker}, "
                    f"speed: {request.speed}}}")
        return self._synthesize(request.text, request.speaker, request.speed)
    
    def _synthesize(self, text: str, speaker: str, speed: float = 1) -> Response:
        """Convert text to speech waveform.
        Args:
          text (str) : Input text to be synthesized
          speed (float)
        """
        # Remove speaker prefix
        speaker = speaker[len(SPEAKER_PREFIX):]

        normalized_text = clean(text, self.model.tts_config.characters.characters)
        wavs = self.model.tts(normalized_text, speaker_name=speaker)
        out = io.BytesIO()
        self.model.save_wav(wavs, out)
        return Response(
            content=ResponseContent(
                audio=out.read(),
                text=text,
                normalized_text=normalized_text,
                sampling_rate=self.sampling_rate,
            )
        )

