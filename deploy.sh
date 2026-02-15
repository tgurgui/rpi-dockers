#!/bin/bash
# 1. Update repository
git pull origin master

# 2. Update all Docker stacks
for d in stacks/*/ ; do
    echo "Updating $d..."
    docker-compose -f "${d}docker-compose.yml" up -d --remove-orphans
done

# 3. Sync DNS records
sudo python3 ./mdns-sync.py