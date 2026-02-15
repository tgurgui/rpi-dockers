# Raspberry Pi 4 Home Server: GitOps & mDNS Sync

This repository manages a containerized home server on a Raspberry Pi 4 (8GB). It uses a GitOps workflow where the repository configuration drives both network routing (Traefik) and local network discovery (mDNS).

## System Architecture
- **Traefik**: Automated Reverse Proxy that routes traffic on Port 80 based on Docker labels.
- **mdns-sync.py**: A run-once Python script that scans Docker labels and publishes `.local` domains to the network.
- **GitOps**: Updates are triggered by pulling the repository and running a deployment script.

---

## 🛠 1. Initial System Setup

### Install Dependencies
Run these commands on the Raspberry Pi:
```bash
sudo apt update
sudo apt install docker-ce avahi-utils python3-pip -y
sudo pip3 install docker
sudo usermod -aG docker $USER
```

### Create the Proxy Network
All containers must join this network to be reachable by Traefik.
```bash
docker network create proxy-nw
```

## 2. Directory Structure
Organize your repository as follows:
```
/my-pi-homelab
├── mdns-sync.py        # The DNS sync script
├── deploy.sh           # The master deployment script
├── backup.sh           # The data backup script
├── README.md
└── stacks/
    ├── gitea/
    ├── portainer/
    ├── qbittorrent/
    └── traefik/
```

## 3. The Deployment Workflow

Use the deploy.sh script to apply changes from Git and refresh DNS records.

## 4. Backups & Maintenance

### Backing up Data
The backup.sh script stops containers, zips the stacks/ directory (where persistent data is stored via bind mounts), and restarts the services.

```bash
#!/bin/bash
BACKUP_DIR="/path/to/your/backup/location"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Stop services for data integrity
docker stop $(docker ps -q)

# Backup data
tar -czf $BACKUP_DIR/pi_backup_$TIMESTAMP.tar.gz ./stacks

# Start services
sudo ./deploy.sh
```

### Cleaning Docker
To prevent the Pi's storage from filling up with old image layers:
```bash
docker system prune -af
```

## 5. Troubleshooting
- **mDNS not resolving**: Run `sudo python3 mdns-sync.py` manually and check for errors.
- **Traefik 404**: Ensure the container is joined to the `proxy-nw` network and the `loadbalancer.server.port` matches the internal port of the application.
- **Name Conflicts**: If you see `name-2.local`, it means an old process didn't die. Run `sudo pkill -f avahi-publish` and then run the sync script again.