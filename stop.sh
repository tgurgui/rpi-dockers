#!/bin/bash

BASE_DIR=$(pwd)
STACKS_DIR="$BASE_DIR/stacks"

for stack in "$STACKS_DIR"/*/; do
    stack_name=$(basename "$stack")
    if [ -f "$stack/docker-compose.yml" ] || [ -f "$stack/docker-compose.yaml" ]; then
        cd "$stack" || continue
        
        docker compose down

        cd "$BASE_DIR"
    fi
done