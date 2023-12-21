# syntax=docker/dockerfile:1
FROM abstract-server

# Installation of pgsql
ARG pg_version=14
RUN apt-get install -y postgresql
RUN pip install psycopg2
ENV pg_version=$pg_version

# Installation of lm-sensors
RUN apt-get install -y lm-sensors

# Last settings
ENV IMAGE_NAME=lpss-server
CMD /usr/sbin/sshd && pg_ctlcluster ${pg_version} main start && nginx && \
	sudo -u www-data gunicorn \
		--access-logfile - \
		--workers 3 \
		--bind unix:/run/gunicorn/gunicorn.sock \
		ru.ihna.kozhukhov.corefacility.wsgi:application
