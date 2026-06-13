#!/bin/bash
echo 0 | sudo -S journalctl -u ollama --since '10 minutes ago' | tail -n 50
free -h
grep Huge /proc/meminfo
