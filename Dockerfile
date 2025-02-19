FROM python:3.12.8-slim-bookworm
LABEL title="chatgpaint"
LABEL authors="Wolfiii, Nicked"
LABEL version="1.0.0"

COPY . /bot

WORKDIR /bot

RUN pip install -r requirements.txt
ENV DOCKER=true
ENV STATUS_UPDATE_PORT=7958

VOLUME ["/db"]
EXPOSE 7958

ENTRYPOINT ["python", "bot.py"]