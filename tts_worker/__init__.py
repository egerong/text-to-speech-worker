import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'TTS')))

from .config import tf_config, mq_config, read_model_config

os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(tf_config.CPP_MIN_LOG_LEVEL)

from .utils import clean, split_sentence
from .synthesizer import Synthesizer
from .mq_consumer import MQConsumer

logger = logging.getLogger(__name__)

