FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm /usr/share/nginx/html/*
COPY index.html /usr/share/nginx/html/index.html
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Expose port 80
EXPOSE 80

# Start all services with our startup script
CMD ["/usr/local/bin/start.sh"]