FROM python:3.14-alpine
RUN apk update \
    && apk upgrade \
    && apk add --no-cache bash \
    py3-pip \
    gcc \
    musl-dev \
    libpq-dev \
    postgresql \
    && rm -rf /var/cache/apk/*
COPY code/requirements.txt /
WORKDIR /app
COPY code/main.py /app/main.py
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh \
    && pip install --upgrade pip setuptools \
    && pip install -r /requirements.txt \
    && pip cache purge
ENTRYPOINT ["/app/entrypoint.sh"]
