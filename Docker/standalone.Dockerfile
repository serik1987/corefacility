# syntax=docker/dockerfile:1
FROM base

# Installation of corefacility
RUN mkdir "/home/sergei_kozhukhov/My Research" && \
	chown sergei_kozhukhov:sergei_kozhukhov "/home/sergei_kozhukhov/My Research"

# Last settings
ENV IMAGE_NAME=standalone
WORKDIR /home/serik1987
CMD corefacility runserver\
	--insecure \
	$(hostname -I | awk '{print $1}'):80 \