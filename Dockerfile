FROM ubuntu:latest

RUN apt-get update -y && apt-get install --fix-missing -y \
    redis-server \
    nginx \
    git \
    nodejs \
    golang \
    libauthen-passphrase-perl \
    libmojolicious-perl \
    libdigest-sha-perl \
    libdbi-perl \
    libdbd-sqlite3-perl \
    libhtml-scrubber-perl \
    libhtml-defang-perl \
    libcrypt-cbc-perl \
    libstring-random-perl \
    python3-pip \
    python3-bcrypt \
    firefox \
    sudo \
    npm \
    php \
    dnsutils \
    xvfb \
    wget \
    unzip
RUN export PERL_MM_USE_DEFAULT=1
RUN cpan CryptX
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install -g bower
COPY frontend-angular /pedagogic_ctf/frontend-angular
RUN cd /pedagogic_ctf/frontend-angular && bower install --allow-root
COPY requirements.txt /pedagogic_ctf/
RUN pip3 install -r /pedagogic_ctf/requirements.txt
COPY sandbox.c sandbox.py clean.py load_challenges.py nginx.conf /pedagogic_ctf/
COPY src /pedagogic_ctf/src
COPY challs /pedagogic_ctf/challs
COPY init.sh run.sh selenium.sh /pedagogic_ctf/
RUN cd /pedagogic_ctf && ./init.sh

CMD service nginx restart && service redis-server restart && /srv/ctf_go/selenium.sh && sudo -u ctf_interne /srv/ctf_go/run.sh
