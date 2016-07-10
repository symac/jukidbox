sudo ifdown eth0
sudo systemctl stop dhcpcd.service
sudo systemctl disable dhcpcd.service
sudo mount -o remount,ro / ; sudo mount -o remount,ro /boot
