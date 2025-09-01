FROM python:3.13-slim

WORKDIR /plex_unmonitorr

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY plex_unmonitorr/ ./plex_unmonitorr/
COPY pyproject.toml .
COPY run.sh .
COPY config.example.yaml .

RUN --mount=type=cache,target=/root/.cache/uv \
    pip install -U pip uv && \
    uv pip install --system .

RUN sed -i 's/\r$//' run.sh && \
    chmod +x run.sh && \
    chmod -R 777 /plex_unmonitorr && \
    chown -R 99:100 /plex_unmonitorr

USER 99:100

CMD ["./run.sh"]
