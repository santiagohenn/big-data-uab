FROM ubuntu
ENV TZ=America/Argentina/Buenos_Aires
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get -y install apache2
COPY index.html /var/www/html/index.html
EXPOSE 80
CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
