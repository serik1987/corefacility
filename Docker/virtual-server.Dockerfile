# syntax=docker/dockerfile:1
FROM abstract-server

# Installation of MySQL Server
RUN apt install -y mysql-server libmysqlclient-dev pkg-config
RUN pip install mysqlclient
RUN chmod a+x /var/run/mysqld

# Last settings
ENV IMAGE_NAME=virtual-server
CMD /usr/sbin/sshd && mysqld -D && nginx && \
	sudo -u www-data gunicorn \
		--access-logfile - \
		--workers 3 \
		--bind unix:/run/gunicorn/gunicorn.sock \
		ru.ihna.kozhukhov.corefacility.wsgi:application