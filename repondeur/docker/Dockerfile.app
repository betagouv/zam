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

# Add base system dependencies
RUN curl -L -O https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb && \
    apt-get update && \
    apt-get -f install --yes --no-install-recommends \
        firefox \
        git \
        locales \
        postgresql-client-10 \
        python3 \
        python3-setuptools \
        python3-pip \
        ./wkhtmltox_0.12.5-1.bionic_amd64.deb \
        xvfb \
    && rm wkhtmltox_0.12.5-1.bionic_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Install Geckodriver to run browser tests in Firefox
RUN curl -L https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz | tar xz -C /usr/local/bin

# Setup french locale
RUN echo 'fr_FR.UTF-8 UTF-8' >> /etc/locale.gen && \
    echo 'LANG="fr_FR.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=fr_FR.UTF-8
ENV LC_ALL=fr_FR.UTF-8
ENV LANG=fr_FR.UTF-8

# Install app and Python dependencies
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN apt-get update && \
    apt-get -f install --yes --no-install-recommends \
        build-essential \
        libpq-dev \
        python3-dev \
    && \
    python3.6 -m pip install --no-cache-dir --src=/src \
        -r requirements.txt \
        -r requirements-dev.txt && \
    apt-get remove --yes \
        build-essential \
        libpq-dev \
        python3-dev \
    && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/apt/lists/*
COPY . ./
RUN python3.6 -m pip install --no-cache-dir --src=/src -e .
