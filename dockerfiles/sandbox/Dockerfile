FROM debian:stretch

RUN apt-get update -y && apt-get install --fix-missing -y \
    sudo \
    build-essential \
    python3 \
    golang-1.7 \
    perl \
    libauthen-passphrase-perl \
    libmojolicious-perl \
    libdigest-sha-perl \
    libdbi-perl \
    libdbd-sqlite3-perl \
    libhtml-scrubber-perl \
    libhtml-defang-perl \
    libcrypt-cbc-perl \
    libstring-random-perl \
    python3-pip 
RUN export PERL_MM_USE_DEFAULT=1
RUN cpan CryptX
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
RUN groupadd code && useradd -g code -d "/home/code" -m code
COPY entrypoint.sh .
COPY run-code.sh .

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
