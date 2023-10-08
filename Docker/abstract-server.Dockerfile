# syntax=docker/dockerfile:1
FROM base

# Installation of the SSH
RUN apt-get install -y openssh-server
RUN mkdir /run/sshd

# Installation of nginx
ARG ubuntu_release=jammy
ARG nginx_gpg_key=ABF5BD827BD9BF62
RUN apt install -y gnupg2
ADD Docker/nginx.list /etc/apt/sources.list.d/nginx.list
RUN sed -i "s/\$release/$ubuntu_release/" /etc/apt/sources.list.d/nginx.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $nginx_gpg_key && apt update && apt install nginx
ADD Docker/nginx.conf /etc/nginx/conf.d/default.conf
RUN mkdir /var/www && mkdir /var/www/static && mkdir /var/www/media;

# Installation of gunicorn
RUN apt install -y gunicorn
RUN mkdir /run/gunicorn && chgrp www-data /run/gunicorn /var/www/media && chmod 0775 /run/gunicorn