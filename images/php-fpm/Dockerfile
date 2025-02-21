FROM ubuntu:20.04

# Disable interactive prompts and update
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y nginx php-fpm && \
    rm -rf /var/lib/apt/lists/*

# Create directories for the mounted apps (they will be overriden by host mounts)
RUN mkdir -p /usr/php-app

COPY php-fpm-nginx.conf /etc/nginx/nginx.conf
COPY index.php /usr/php-app/index.php
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Expose nginx's default port
EXPOSE 80

# Start all services with our startup script
CMD ["/usr/local/bin/start.sh"]