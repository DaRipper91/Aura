#!/bin/bash
# 1. Enable IP Forwarding
echo 0 | sudo -S sysctl -w net.ipv4.ip_forward=1

# 2. Setup NAT (Masquerade)
# wlp0s20u6 = Wi-Fi
# enp0s20u2 = USB Phone
echo 0 | sudo -S iptables -t nat -A POSTROUTING -o wlp0s20u6 -j MASQUERADE
echo 0 | sudo -S iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
echo 0 | sudo -S iptables -A FORWARD -i enp0s20u2 -o wlp0s20u6 -j ACCEPT

# 3. Prevent sleep on Da-HP (The Hub)
echo 0 | sudo -S systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
