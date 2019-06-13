FROM ubuntu:18.04
RUN apt update && apt install -y --upgrade python3 python3-pip && apt autoremove -y && apt clean
COPY main.py /srv/main.py
ENTRYPOINT ['python3', '/srv/main.py']