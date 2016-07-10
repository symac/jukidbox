#!/bin/sh
sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot
sudo systemctl enable dhcpcd.service
sudo systemctl start dhcpcd.service
sudo ifup eth0
