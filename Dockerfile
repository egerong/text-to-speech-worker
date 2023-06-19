# FROM python:3.9

ARG BASE=nvidia/cuda:11.8.0-base-ubuntu22.04
FROM ${BASE}


# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    software-properties-common
        # swig \
        # gcc \
        # g++ \
        # libffi-dev \
        # musl-dev \
        # git
RUN add-apt-repository ppa:deadsnakes/ppa

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    python3.9 \
    python3.9-venv \
    # python3-pip \
    swig


ENV PYTHONIOENCODING=utf-8
ENV MKL_NUM_THREADS=16

WORKDIR /app

RUN adduser --disabled-password --gecos "app" app && \
    chown -R app:app /app
USER app

# ENV PATH="/home/app/.local/bin:${PATH}"

RUN python3.9 -m venv venv
ENV PATH="/app/venv/bin:${PATH}"

COPY --chown=app:app requirements.txt .
RUN pip3 install -r requirements.txt && \
    rm requirements.txt

COPY --chown=app:app . .

RUN python3.9 -m pip  && sleep 10

ENTRYPOINT ["python", "main.py"]
