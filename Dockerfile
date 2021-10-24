FROM ubuntu:20.04

RUN apt update && DEBIAN_FRONTEND="noninteractive" apt install -y python3 python3-pip libpython3.8-dev gcc

WORKDIR /var/www/flicks

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt && pip3 install --upgrade setuptools

RUN apt remove -y python3-pip && apt autoremove -y

COPY . .
