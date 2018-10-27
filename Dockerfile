FROM ubuntu:18.04
MAINTAINER Artem Svetlov <trolleway@yandex.ru>
RUN apt-get update
RUN apt-get install -y python \
python-pip \
git \
software-properties-common
RUN pip install -y --upgrade pip
RUN apt-add-repository -y ppa:nextgis/ppa
RUN apt-get update
RUN apt-get install -y gdal-bin python-gdal

RUN git clone https://github.com/trolleway/openimagerynetwork-download.git
WORKDIR openimagerynetwork-download

RUN pip install -r requirements.txt


