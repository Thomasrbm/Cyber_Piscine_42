FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    tor \
    openssh-server \
    php-fpm \
    php-sqlite3 \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# --- Configs ---
COPY nginx.conf    /etc/nginx/nginx.conf
COPY sshd_config   /etc/ssh/sshd_config
COPY torrc         /etc/tor/torrc

# --- Web content ---
COPY www/          /var/www/html/
RUN mkdir -p /var/www/data \
    && chown -R www-data:www-data /var/www

# --- SSH setup ---
RUN mkdir -p /run/sshd /root/.ssh && chmod 700 /root/.ssh
COPY ssh/authorized_keys /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

# Regenerate hostkeys: Ed25519 only (drop RSA/ECDSA)
RUN rm -f /etc/ssh/ssh_host_*_key* \
    && ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ""

# --- Tor hidden service dir ---
RUN mkdir -p /var/lib/tor/hidden_service \
    && chown -R debian-tor:debian-tor /var/lib/tor \
    && chmod 700 /var/lib/tor/hidden_service

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
