# Estonian Text-to-Speech

This repository contains Estonian multi-speaker neural text-to-speech synthesis workers that process requests from
RabbitMQ.

The project is developed by the [Institute of Estonian Language](https://www.eki.ee) and is based on the work of the [NLP research group](https://tartunlp.ai) at the [University of Tartu](https://ut.ee).

Speech synthesis can also be tested in our [demo](https://www.eki.ee/heli).

## Models

[The releases section](https://github.com/egerong/text-to-speech-worker/releases) contains the model files or their
download instructions. If a release does not specify the model information, the model from the previous release can
be used. We advise always using the latest available version to ensure best model quality and code compatibility.

The model configuration files included in `config/config.yaml` correspond to the following `models/` directory
structure:

```
models
└── merlin
    └── [VOICE]
        ├── acoustic_model
        └── duration_model
```

## Setup

The TTS worker can be deployed using the docker image published alongside the repository. Each image version correlates
to a specific release. The required model file(s) are excluded from the image to reduce the image size and should be
downloaded from the releases section and their directory should be attached to the volume `/app/models`.

Logging configuration is loaded from `/app/config/logging.prod.ini` and service configuration from the
`/app/config/config.yaml` file. The included config is commented to illustrate how new model configurations could be
added.

The following environment variables should be configured when running the container:

- `MQ_USERNAME` - RabbitMQ username
- `MQ_PASSWORD` - RabbitMQ user password
- `MQ_HOST` - RabbitMQ host
- `MQ_PORT` (optional) - RabbitMQ port (`5672` by default)
- `MQ_EXCHANGE` (optional) - RabbitMQ exchange name (`text-to-speech` by default)
- `MQ_HEARTBEAT` (optional) - heartbeat interval (`60` seconds by default)
- `MQ_CONNECTION_NAME` (optional) - friendly connection name (`TTS worker` by default)
- `MERLIN_TEMP_DIR` (optional) - directory for storing temporary files, in-memory filesystem recommended (`mrln_et_light/temp` by default)

By default, the container entrypoint is `main.py` without additional arguments, but arguments should be defined with the
`COMMAND` option. The only required flag is `--model-name` to select which model is loaded by the worker. The full list
of supported flags can be seen by running `python main.py -h`:

```commandline
usage: main.py [-h] [--model-config MODEL_CONFIG] [--model-name MODEL_NAME] [--log-config LOG_CONFIG]

A text-to-speech worker that processes incoming TTS requests via RabbitMQ.

optional arguments:
  -h, --help            show this help message and exit
  --model-config MODEL_CONFIG
                        The model config YAML file to load.
  --model-name MODEL_NAME
                        The model to load. Refers to the model name in the config file.
  --log-config LOG_CONFIG
                        Path to log config file.
```

The setup can be tested with the following sample `docker-compose.yml` configuration:

```yaml
version: '3'
services:
  rabbitmq:
    image: 'rabbitmq'
    environment:
      - RABBITMQ_DEFAULT_USER=${RABBITMQ_USER}
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASS}
  tts_api:
    image: ghcr.io/tartunlp/text-to-speech-api:3.0.0
    environment:
      - MQ_HOST=rabbitmq
      - MQ_PORT=5672
      - MQ_USERNAME=${RABBITMQ_USER}
      - MQ_PASSWORD=${RABBITMQ_PASS}
    ports:
      - '8000:8000'
    volumes:
      - ./config/api_config.yaml:/app/config/config.yaml
    depends_on:
      - rabbitmq
  tts_worker:
    image: ghcr.io/egerong/text-to-speech-worker:merlin-3.0.1
    environment:
      - MQ_HOST=rabbitmq
      - MQ_PORT=5672
      - MQ_USERNAME=${RABBITMQ_USER}
      - MQ_PASSWORD=${RABBITMQ_PASS}
      - MERLIN_TEMP_DIR=/tmp
    command: [ "--model-name", "merlin" ]
    tmpfs:
      - /tmp
    volumes:
      - ./models/merlin:/app/mrln_et_light/voices/
    depends_on:
      - rabbitmq
```

### Manual setup

The following steps have been tested on Ubuntu and is both CPU and GPU compatible (CUDA required).

- Clone this repository with submodules
- Install prerequisites:
    - GNU Compiler Collection (`sudo apt install build-essential`)
    - For a **CPU** installation we recommend using the included `requirements.txt` file in a clean environment (tested with
      Python 3.6)
      ```commandline
      pip install -r requirements.txt
      ```


- Download the models from the [releases section](https://github.com/egerong/text-to-speech-worker/releases) and
  place inside the `mrln_et_light/voices` directory.

- Specify RabbitMQ connection parameters with environment variables or in a `config/.env` file as illustrated in the
  `config/sample.env`.

Run the worker with where `MODEL_NAME` matches the model name in your config file:

```commandline
python main.py --model-name $MODEL_NAME [--log-config config/logging.ini --config config/config.yaml]
```
