FROM python:3.13-slim

WORKDIR /home/docker

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY plex_unmonitorr/ ./plex_unmonitorr/
COPY pyproject.toml .
COPY run.sh .

RUN --mount=type=cache,target=/root/.cache/uv \
    pip install -U pip uv && \
    uv pip install --system .

RUN chmod -R 777 /home/docker && \
    chown -R 99:100 /home/docker

USER 99:100

CMD ["./run.sh"]
