FROM python:3.6

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        gcc \
        g++ \
        libffi-dev \
        musl-dev \
        git \
        # For Merlin
        build-essential \
        csh \
        automake \
        sox

ENV PYTHONIOENCODING=utf-8
ENV MKL_NUM_THREADS=16

WORKDIR /app

RUN adduser --disabled-password --gecos "app" app && \
    chown -R app:app /app
USER app

ENV PATH="/home/app/.local/bin:${PATH}"

RUN pip install --upgrade pip
COPY --chown=app:app requirements.txt .
RUN pip install --user -r requirements.txt && \
    rm requirements.txt
RUN pip install --user bandmat

COPY --chown=app:app mrln_et_light/tools mrln_et_light/tools
RUN cd mrln_et_light/tools && \
    sh compile_tools.sh && \
    cd ../..

COPY --chown=app:app mrln_et_light/__init__.py mrln_et_light/merlin.py mrln_et_light/
COPY --chown=app:app mrln_et_light/src mrln_et_light/src
COPY --chown=app:app tts_preprocess_et tts_preprocess_et
COPY --chown=app:app tts_worker tts_worker
COPY --chown=app:app main.py .
COPY --chown=app:app config config

# RUN ls -la /app && sleep 100

ENTRYPOINT ["python", "main.py"]
