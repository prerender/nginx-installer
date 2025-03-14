FROM nginx:latest

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy vhost configurations
COPY conf.d /etc/nginx/conf.d

# Expose ports
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
