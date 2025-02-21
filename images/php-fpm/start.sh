#!/bin/bash
set -e

cleanup() {
    echo "Signal received, shutting down services..."
    echo "Stopping nginx..."
    nginx -s quit
    echo "Stopping PHP-FPM..."
    service php7.4-fpm stop
    echo "Killing background processes..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT

# Start PHP-FPM service
echo "Starting PHP-FPM..."
service php7.4-fpm start

# Wait a moment for the socket to be created, then adjust its permissions
sleep 1
echo "Setting permissions for PHP-FPM socket..."
chmod 666 /var/run/php/php7.4-fpm.sock

# Tail Nginx logs to stdout in the background
echo "Tailing Nginx access and error logs to stdout..."
tail -n 0 -F /var/log/nginx/access.log /var/log/nginx/error.log &

# Start nginx in the foreground (run in the background and wait below)
echo "Starting nginx..."
nginx -g "daemon off;" &

# Wait for background processes (nginx and tail) to exit
wait