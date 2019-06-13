FROM ubuntu:18.04
RUN apt-get update && apt-get install -y --upgrade python3 python3-pip && apt-get autoremove -y && apt-get clean
ADD main.py /srv/main.py
CMD python3 /srv/main.py