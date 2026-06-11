#!/bin/bash
set -e

# Start PHP-FPM
service php8.2-fpm start

# Start Nginx
service nginx start

# Start SSH
service ssh start

# Print the .onion URL once Tor publishes it (background watcher)
(
    while [ ! -f /var/lib/tor/hidden_service/hostname ]; do sleep 1; done
    echo ""
    echo "==============================================="
    echo "Onion URL: $(cat /var/lib/tor/hidden_service/hostname)"
    echo "==============================================="
    echo ""
) &

# Start Tor in foreground (PID 1 of container)
exec sudo -u debian-tor tor -f /etc/tor/torrc
