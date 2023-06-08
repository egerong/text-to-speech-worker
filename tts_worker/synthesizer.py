from typing import Tuple

import io
import logging
import re

import numpy as np
# from scipy.io import wavfile
from nltk import sent_tokenize

# import tensorflow as tf
# from tensorflow.python.framework.errors_impl import InvalidArgumentError

from tts_worker.config import ModelConfig
from tts_worker.schemas import Request, Response, ResponseContent
from tts_worker.utils import clean, split_sentence

# from tts_worker.vocoding.predictors import HiFiGANPredictor

from mrln_et_light.merlin import MerlinSynthesizer

logger = logging.getLogger(__name__)

speaker_ids = {
    0: 'eki_et_ind16k',
    1: 'eki_et_kyl16k',
    2: 'eki_et_lee16k',
    3: 'eki_et_lsi16k',
    4: 'eki_et_lvk16k',
    5: 'eki_et_ptr16k',
    6: 'eki_et_rna16k',
    7: 'eki_et_tmb16ko',
    8: 'eki_et_tmb16ky',
    9: 'eki_et_tnu16k',
}

class Synthesizer:
    def __init__(self, model_config: ModelConfig, max_input_length: int = 0):
        self.model_name = model_config.model_name

        self.model = MerlinSynthesizer(merlin_path=model_config.model_path)
       
        self.speakers = model_config.speakers

        self.frontend = model_config.frontend

        self.sampling_rate = 16000 # TODO: make this configurable

        

        # model_input_limit = self.model.config['encoder_max_position_encoding'] - self.gst_len

        # if max_input_length and max_input_length <= model_input_limit:
        #     logger.info(f"Max input length set according to user configuration: {max_input_length}")
        #     self.max_input_length = max_input_length
        # else:
        #     if max_input_length > model_input_limit:
        #         logger.warning("The specified input length limit exceeds the model's maximum input size.")
        #     self.max_input_length = model_input_limit
        #     self._find_max_input_length()

        logger.debug(f"sampling rate: {self.sampling_rate}, ")

        logger.info("Merlin synthesizer initialized.")


    def process_request(self, request: Request) -> Response:
        logger.info(f"Request received: {{"
                    f"speaker: {request.speaker}, "
                    f"speed: {request.speed}}}")
        response, _ = self._synthesize(request.text, request.speaker, request.speed)
        return response

    def _synthesize(self, text: str, speaker: str, speed: float = 1) -> Tuple[Response, int]:
        """Convert text to speech waveform.
        Args:
          text (str) : Input text to be synthesized
          speed (float)
        """
        max_input_length = 0 # TODO
        waveforms = []
        voice = speaker_ids[self.speakers[speaker].speaker_id]
        wavBytes = self.model.synthesize(text, voice=voice)

        result = Response(
            content=ResponseContent(
                audio=wavBytes,
                text=text,
                normalized_text=text, # TODO: find normalized text from Merlin
            )
        )
        return result, max_input_length
