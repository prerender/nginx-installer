#!/bin/bash
set -e

cleanup() {
    echo "Signal received, shutting down services..."
    echo "Stopping nginx..."
    nginx -s quit
    echo "Stopping Node.js app..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT

# Start Node.js application
echo "Starting Node.js app..."
node /usr/src/app/app.js &

# Tail Nginx logs and Node.js logs to stdout in the background
echo "Tailing Nginx access, error logs, and Node.js logs to stdout..."
tail -n 0 -F /var/log/nginx/access.log /var/log/nginx/error.log /usr/src/app/logs/app.log &

# Start nginx in the foreground (run in the background and wait below)
echo "Starting nginx..."
nginx -g "daemon off;" &

# Wait for background processes (nginx and tail) to exit
wait
