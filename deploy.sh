#!/bin/bash
# 1. Update repository
git pull origin master

# 2. Create network
NETWORK_NAME="proxy-nw"
if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
    docker network create $NETWORK_NAME
fi

# 3. Update all Docker stacks
# Get the absolute path of the directory where this script is located
BASE_DIR=$(pwd)
STACKS_DIR="$BASE_DIR/stacks"

for stack in "$STACKS_DIR"/*/; do
    stack_name=$(basename "$stack")
    if [ -f "$stack/docker-compose.yml" ] || [ -f "$stack/docker-compose.yaml" ]; then
        echo "----------------------------------------------------"
        echo "Deploying Stack: $stack_name"
        cd "$stack" || continue
        
        docker compose up -d --remove-orphans

        cd "$BASE_DIR"
    fi
done

# 4. Sync DNS records
sudo python3 ./mdns-sync.py
