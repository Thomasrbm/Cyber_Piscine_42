# ft_onion

Web service hidden on the Tor network. 42 Cybersecurity Piscine.

## Stack

- **Debian bookworm-slim** as base image
- **Tor** for the hidden service (v3 .onion address)
- **Nginx** serving static + PHP via FastCGI
- **PHP-FPM** with SQLite for the guestbook bonus app
- **OpenSSH** hardened (Ed25519 only, key auth only, port 4242)

## Setup

1. Add your SSH public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub > ssh/authorized_keys
   ```

2. Build and run:
   ```bash
   docker compose up -d --build
   ```

3. Get the .onion URL (Tor takes ~30s to publish on first start):
   ```bash
   docker exec ft_onion cat /var/lib/tor/hidden_service/hostname
   ```

4. Open the URL in [Tor Browser](https://www.torproject.org/download/).

## SSH access

SSH is exposed on port 4242 via the same .onion address (no IP exposure).

```bash
torsocks ssh -p 4242 root@<your-address>.onion
```

## Files

| File              | Purpose                              |
|-------------------|--------------------------------------|
| `Dockerfile`      | Container image definition           |
| `docker-compose.yml` | Persistent volumes (Tor keys + DB)|
| `nginx.conf`      | Web server (binds 127.0.0.1:80)      |
| `sshd_config`     | SSH (port 4242, hardened)            |
| `torrc`           | Tor hidden service v3                |
| `start.sh`        | Launches php-fpm, nginx, ssh, tor    |
| `www/index.html`  | Mandatory static landing page        |
| `www/guestbook/`  | Bonus interactive PHP app            |
| `ssh/authorized_keys` | Your SSH public key              |

## Design choices

- **No firewall, no open ports**: all services bind to `127.0.0.1`. Only Tor reaches them, externally everything is invisible.
- **Single .onion for HTTP + SSH**: one HiddenServiceDir, two HiddenServicePorts. Cleaner.
- **Persistent Tor volume**: keeps the .onion address stable across rebuilds.
- **Ed25519-only SSH**: removed RSA/ECDSA host keys, modern crypto only.
- **No password auth**: pubkey only, root login restricted to keys.

## Stopping

```bash
docker compose down       # stop, keep volumes (.onion stable)
docker compose down -v    # stop + wipe volumes (new .onion next time)
```
