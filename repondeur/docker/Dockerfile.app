FROM python:3.6.6

# Add APT repo for Postgres 10.x
RUN apt-get update && apt-get install --yes apt-transport-https && rm -rf /var/lib/apt/lists/*
RUN curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1 apt-key add -
RUN echo "deb https://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && apt-get install --yes \
    libpq-dev \
    locales \
    postgresql-client-10 \
    wkhtmltopdf \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN echo 'fr_FR.UTF-8 UTF-8' >> /etc/locale.gen && \
    echo 'LANG="fr_FR.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=fr_FR.UTF-8

WORKDIR /app

RUN python3.6 -m pip install pipenv==2018.7.1

COPY . .
RUN pipenv install --dev --deploy

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
