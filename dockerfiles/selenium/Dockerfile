FROM debian:testing

RUN apt-get update -y && apt-get install --fix-missing -y \
    sudo \
    redis-server \
    firefox-esr \
    python3 \
    python3-pip \
    xvfb \
    wget
COPY requirements.txt /
RUN pip3 install -r /requirements.txt

RUN groupadd selenium && useradd -g selenium -d "/home/selenium" -m selenium
COPY init.sh /init.sh
RUN chmod +x /init.sh
RUN /init.sh
COPY api.py /home/selenium/
COPY worker.py /home/selenium/
COPY browser.py /home/selenium/
RUN chown -R selenium:selenium /home/selenium/
ADD entrypoint.sh entrypoint.sh
RUN sed -i -e"s/^bind\s*127.0.0.1/bind 0.0.0.0/" /etc/redis/redis.conf

EXPOSE 6379
EXPOSE 8888

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
