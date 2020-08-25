FROM python:3

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /config

CMD [ "python3", "-u", "flathunt.py", "-c", "/config/config.yaml" ]
