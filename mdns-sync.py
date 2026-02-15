#!/usr/bin/env python3
import docker
import subprocess
import re
import socket
import os
import sys

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def clean_slate():
    print("[!] Clearing old mDNS records...")
    # Kill any existing background publishers
    subprocess.run(["sudo", "pkill", "-f", "avahi-publish"], stderr=subprocess.DEVNULL)
    # Flush Avahi cache
    subprocess.run(["sudo", "systemctl", "restart", "avahi-daemon"], check=True)

def extract_hosts(labels):
    hosts = []
    for key, value in labels.items():
        if key.startswith("traefik.http.routers.") and ".rule" in key:
            found = re.findall(r"Host\([`'\"](.*?)[`'\"]\)", value)
            for h in found:
                if h.endswith(".local"):
                    hosts.append(h)
    return list(set(hosts))

def main():
    #if os.geteuid() != 0:
    #    print("[!] This script must be run with sudo to manage Avahi processes.")
    #    sys.exit(1)

    clean_slate()
    PI_IP = get_ip()
    client = docker.from_env()
    
    containers = client.containers.list()
    found_count = 0

    for container in containers:
        hosts = extract_hosts(container.labels)
        for host in hosts:
            print(f"[+] Publishing {host} -> {PI_IP} (Container: {container.name})")
            # We use nohup and redirect output to truly detach the process
            cmd = f"nohup avahi-publish -a -R {host} {PI_IP} > /dev/null 2>&1 &"
            subprocess.Popen(cmd, shell=True)
            found_count += 1

    print(f"\n[✓] Sync complete. {found_count} records published in background.")

if __name__ == "__main__":
    main()