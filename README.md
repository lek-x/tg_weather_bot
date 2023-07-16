# Telegram Weather bot with CI/CD deploying pipline.

## Description:
This repo contains Python code of telegram bot and CI/CD code for deployig in dev/prod environments:

## Bot telegram id [PROD version]

https://t.me/weather_rms_bot


## About App:
It is a python based app Telegram bot

## Features:

- **Free weather API** - bot uses free Open Weather API

- **Weather autosend function** - bot sends  Weather at desired time.




## Requrements:
  - Linux based OS
  - Terraform >= 1.0
  - Docker
  - Anchore Grype tool
  - HashiCorp Vault
  - HashiCorp Nomad
  - Github runner
  - poetry
  - Python > 3.7
  - pip


```mermaid
---
title: Scheme
---
graph TD
  X[user]
  subgraph A[GitHuB]
    B[Repository]
  end
  subgraph C[Linux VM]
    direction TB
    subgraph D[NOMAD Cluster]
        E[PostgreSQL 15]
        F[Weather Bot]
        F <-.Storing data.-> E
    end
    F -- Get secrets and vars --> G
    E -- Get secrets and vars-->G
    D -- Get images-->A
    subgraph G[Vault]
        H[Secret1]
        J[Secret2]
        K[SecretN]
    end
  end
  X <--> F
```

```mermaid
---
title: CI/CD Environments Logic
---
flowchart LR;
 A[On push to DEV] --> B[Auto Deploy to Dev]
 C[On PR merged into main] --> E[Nomad Plan]-->D[Auto start PROD deploying]
```


```mermaid
---
title: DEV/PROD Pipeline steps
---
flowchart LR;
A[Clean curent directory + \ndocker system prune] --> B[Checkout] --> C[Building Docker Image\n and push to registry] --> D[Check image\nby Anchore Grype] --> E[Rendering Terraform template\n for Nomad] -->F[Nomad job run]

```


## Main files:
1. Dockerfile - to build app
2. main.py - app core
3. .github/ - CI/CD workflow
4. bot.tpl - terraform template
5. entrypoint.sh - entrypoint for container
6. main.tf - terraform main file
7. .pre-commit-config.yml - config for pre-commit tool
8. requiremenets.txt - python packages for app

## Quick start:
TBD


## Known bugs and limitations
1. Hourly weather may show the wrong hour, will be fixed in next releases.
2. It is small possibility that bot sends auto message twice, default check interval 58 seconds.


## License
GNU GPL v3
