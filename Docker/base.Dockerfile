# syntax=docker/dockerfile:1
FROM ubuntu:latest

# Standard Ubuntu settings
RUN apt-get update && apt-get -y upgrade && apt-get install -yq tzdata sudo
RUN ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN useradd -m sergei_kozhukhov
RUN echo "sergei_kozhukhov:admin-password" | chpasswd

# Installation of python
RUN apt-get install -y python3.11 python3-pip python3-dev libpq-dev
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
	ln -sf /usr/bin/pygettext3.11 /usr/bin/pygettext3 && \
	ln -sf /usr/bin/pydoc3.11 /usr/bin/pydoc3 && \
	ln -sf /usr/bin/python3 /usr/bin/python && \
	ln -sf /usr/include/python3.10 /usr/include/python3.11
RUN pip install psutil python-dotenv django django-configurations djangorestframework pillow  parameterized pytz \
	colorama urllib3 bs4 dateutils numpy matplotlib scipy