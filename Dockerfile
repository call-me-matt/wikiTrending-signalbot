FROM python
ENV SIGNAL_CLI_VERSION=0.7.4

WORKDIR /app/

RUN wget https://github.com/AsamK/signal-cli/releases/download/v$SIGNAL_CLI_VERSION/signal-cli-$SIGNAL_CLI_VERSION.tar.gz

RUN tar -xzvf signal-cli-$SIGNAL_CLI_VERSION.tar.gz \
    && rm signal-cli-$SIGNAL_CLI_VERSION.tar.gz \
    && mv signal-cli-$SIGNAL_CLI_VERSION signal-cli

RUN apt-get update
RUN apt-get install -y openjdk-11-jre-headless

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./docker/entrypoint.sh /app/
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
