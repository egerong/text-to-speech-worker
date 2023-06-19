# Estonian Text-to-Speech

This repository contains Estonian multi-speaker neural text-to-speech synthesis workers that process requests from
RabbitMQ.

The project is developed by the [Institute of the Estonian Language](https://www.eki.ee) and is based on the work of the [NLP research group](https://tartunlp.ai) at the [University of Tartu](https://ut.ee).

Speech synthesis can also be tested in our [demo](https://www.eki.ee/heli).

## Models

[The releases section](https://github.com/keeleinstituut/text-to-speech-worker/releases) contains the model files or their
download instructions. If a release does not specify the model information, the model from the previous release can
be used. We advise always using the latest available version to ensure best model quality and code compatibility.

The model configuration files included in `config/config.yaml` correspond to the following `models/` directory
structure:

```
models
└── vits
    ├── config.json
    ├── model.pth
    ├── speakers.pth
    └── speakers_aggr.pth
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
- `MKL_NUM_THREADS` (optional) - number of threads used for intra-op parallelism by PyTorch
  . `16` by default. If set to a blank value, it defaults to the number of CPU cores which may cause computational
  overhead when deployed on larger nodes. Alternatively, the `docker run` flag `--cpuset-cpus` can be used to control
  this.
  section below.

GPU support requires CUDA >= 11.8. Refer to the [NVIDIA documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)

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
