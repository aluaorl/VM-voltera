FROM python:3.11.9

# Установка необходимых утилит (включая openssl) для подключения репозиториев Microsoft
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-archive-keyring.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# Установка ODBC Driver 18 для SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt

RUN pip3 install --no-cache-dir -r /requirements.txt
RUN pip3 install gunicorn

COPY ./app.py /code/
COPY ./calculation_engine.py /code/
COPY ./expression_parser.py /code/
COPY ./db_manager.py /code/
COPY ./crypto_manager.py /code/
COPY ./components /code/components/
RUN mkdir /code/assets
COPY ./assets/ /code/assets/

WORKDIR /code/
ENV PYTHONPATH /code

ENV GUNICORN_CMD_ARGS "--bind=0.0.0.0:8080 --workers=2 --threads=4 --worker-class=gthread --timeout=300 --forwarded-allow-ips='*' --access-logfile -"

CMD ["gunicorn", "app:server"]