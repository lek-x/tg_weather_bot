FROM python:3.12.0a3-alpine3.17
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
ENV bottoken=$bottoken
ENV weathertok=$weathertok
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_DB=$POSTGRES_DB
EXPOSE 80 88 443 8443
ENTRYPOINT ["python", "/app/main.py"]


