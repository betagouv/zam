FROM ubuntu:18.04

# Add APT repo for Postgres 10.x
RUN apt-get update && \
    apt-get install --yes \
        curl \
        apt-transport-https \
        gnupg \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1 apt-key add -
RUN echo "deb https://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN curl -L -O https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb && \
    apt-get update && \
    apt-get -f install --yes \
        git \
        libpq-dev \
        locales \
        postgresql-client-10 \
        python3 \
        python3-pip \
        ./wkhtmltox_0.12.5-1.bionic_amd64.deb \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN echo 'fr_FR.UTF-8 UTF-8' >> /etc/locale.gen && \
    echo 'LANG="fr_FR.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=fr_FR.UTF-8

ENV LC_ALL=fr_FR.UTF-8
ENV LANG=fr_FR.UTF-8

WORKDIR /app

RUN python3.6 -m pip install pipenv==2018.7.1

COPY . .

RUN pipenv lock -r >requirements.txt && \
    python3.6 -m pip install --src=/src -r requirements.txt && \
    pipenv lock -r --dev >requirements-dev.txt && \
    python3.6 -m pip install --src=/src -r requirements-dev.txt

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
