# Dockerfile (debian slim)
FROM debian:stable-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip nasm binutils make && \
    rm -rf /var/lib/apt/lists/*
# usuario no root
RUN useradd -ms /bin/bash student
USER student
WORKDIR /work
COPY . /work
# Ejemplo: make run
