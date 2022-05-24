FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONIOENCODING=utf-8

# install packages
RUN apt-get update -y
RUN apt-get install -y apt-utils
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-opencv
RUN apt-get install -y python3-tk
RUN apt-get install -y python3-pyqt5
RUN apt-get install -y cmake
RUN apt-get install -y curl
RUN apt-get install -y unzip
RUN apt-get install -y vim

RUN mkdir /api
RUN mkdir /var/log/uwsgi

WORKDIR /api

ADD ./src /api

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "/bin/bash" ]
