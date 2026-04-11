FROM python:3.12-alpine
RUN apk update \
    && apk upgrade \
    && apk add --no-cache bash \
    py3-pip \
    gcc \
    musl-dev \
    libpq-dev \
    postgresql \
    && rm -rf /var/cache/apk/*
COPY requirements.txt /
WORKDIR /app
COPY ["main.py","entrypoint.sh", "./"]
RUN chmod +x /app/entrypoint.sh \
    && pip install --upgrade pip setuptools \
    && pip install -r /requirements.txt \
    && pip cache purge
ENTRYPOINT ["/app/entrypoint.sh"]
