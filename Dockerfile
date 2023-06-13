FROM python:3.9

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        gcc \
        g++ \
        libffi-dev \
        musl-dev \
        git

ENV PYTHONIOENCODING=utf-8
ENV MKL_NUM_THREADS=16

WORKDIR /app

RUN adduser --disabled-password --gecos "app" app && \
    chown -R app:app /app
USER app

ENV PATH="/home/app/.local/bin:${PATH}"

COPY --chown=app:app requirements.txt .
RUN pip install --user -r requirements.txt && \
    rm requirements.txt

COPY --chown=app:app TTS TTS

RUN pip install -e TTS

COPY --chown=app:app . .

ENTRYPOINT ["python", "main.py"]
