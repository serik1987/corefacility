# syntax=docker/dockerfile:1
FROM ubuntu:latest

# Standard Ubuntu settings
RUN apt-get update && apt-get -y upgrade && apt-get install -yq tzdata sudo
RUN ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN useradd -m sergei_kozhukhov
RUN echo "sergei_kozhukhov:admin-password" | chpasswd

# Installation of python
RUN apt-get install -y python3 python3-dev python3-pip libpq-dev git

# Running the server
CMD tail -f >/dev/null