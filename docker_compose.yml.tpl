---

services:
  bot:
    image: ${repo}/lek-x/${image_name}:${ver}
    container_name: "bot${JOB_ENV}"
    hostname: "bot-${JOB_ENV}"
    environment:
        BOT_TOKEN: "${BOT_TOKEN}"
        POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
        POSTGRES_USER: "${POSTGRES_USER}"
        POSTGRES_DB: "${POSTGRES_DB}"
        POSTGRES_PORT: "${POSTGRES_PORT}"
        POSTGRES_HOST: "db-${JOB_ENV}"
    restart: unless-stopped

  db-${JOB_ENV}:
    image: postgres:15.2-alpine
    container_name: db-${JOB_ENV}
    hostname: db-${JOB_ENV}
    ports:
      - "5432:5432"
    volumes:
      - postgres-${JOB_ENV}:/var/lib/postgresql/data
    environment:
        POSTGRES_DB: "${POSTGRES_DB}"
        POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
        POSTGRES_USER: "${POSTGRES_USER}"
        PGPORT: "${POSTGRES_PORT}"
    restart: unless-stopped

volumes:
  postgres-${JOB_ENV}:
