---

services:
  bot-${JOB_ENV}:
    image: ghcr.io/${repo}/${image_name}:${ver}
    container_name: "bot-${JOB_ENV}"
    hostname: "bot-${JOB_ENV}"
    environment:
        BOT_TOKEN: "${BOT_TOKEN}"
        POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
        POSTGRES_USER: "${POSTGRES_USER}"
        POSTGRES_DB: "${POSTGRES_DB}"
        POSTGRES_PORT: "${POSTGRES_PORT}"
        POSTGRES_HOST: "db-${JOB_ENV}"
        %{if JOB_ENV == "dev"}
        WEATHER_BOT_LOG_ENABLED=true
        WEATHER_BOT_LOG_LEVEL=DEBUG
        %{endif}
    restart: unless-stopped
    depends_on:
      - db-${JOB_ENV}
    mem_limit: 512M
    cpus: "0.5"


  db-${JOB_ENV}:
    image: postgres:18-alpine
    container_name: db-${JOB_ENV}
    hostname: db-${JOB_ENV}
    ports:
      - "${POSTGRES_PORT}"
    volumes:
      - postgres-${JOB_ENV}:/var/lib/postgresql/data
    environment:
        POSTGRES_DB: "${POSTGRES_DB}"
        POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
        POSTGRES_USER: "${POSTGRES_USER}"
        PGPORT: "${POSTGRES_PORT}"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 10s
    mem_limit: 1G
    cpus: "1.0"


volumes:
  postgres-${JOB_ENV}:

networks:
  weatherbot-${JOB_ENV}:
