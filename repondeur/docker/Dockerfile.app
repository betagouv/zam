FROM python:3.6.6

RUN apt-get update && apt-get install --yes \
    libpq-dev \
    locales \
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
