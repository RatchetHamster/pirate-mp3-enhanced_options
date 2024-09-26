#/!bin/bash

sudo apt update
sudo apt upgrade
sudo apt install samba samba-common-bin

echo "[pirateMP3]" >> /etc/samba/smb.conf
echo "path = /home/pi/pirate-mp3-enhanced_options/music" >> /etc/samba/smb.conf
echo "writeable = yes" >> /etc/samba/smb.conf
echo "browseable = yes" >> /etc/samba/smb.conf
echo "public=no" >> /etc/samba/smb.conf

pass=123
(echo "$pass"; echo "$pass") | smbpasswd -s -a pi
sudo systemctl restart smbd
