FROM python:3.10.4-alpine3.15

ENV LANG C.UTF-8

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        python3-dev \
        build-base \
        gcc \
        libc-dev \
        libffi-dev \
        git \
        jsonnet && \
    pip install PyGithub GitPython requests

COPY lib/github-committer.py /github-committer.py
