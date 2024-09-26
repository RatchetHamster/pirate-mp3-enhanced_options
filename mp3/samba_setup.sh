#/!bin/bash

sudo apt update
sudo apt upgrade
sudo apt install samba samba-common-bin

#mkdir ~/shared #May need to be modified to give pi access as this will be made with sudo

function add_to_config_text {
    CONFIG_LINE="$1"
    CONFIG="$2"
    sed -i "s/^#$CONFIG_LINE/$CONFIG_LINE/" $CONFIG
    if ! grep -q "$CONFIG_LINE" $CONFIG; then
		printf "$CONFIG_LINE\n" >> $CONFIG
    fi
}

add_to_config_text "[pirateMP3]" /etc/samba/smb.conf
add_to_config_text "path = /home/pi/pirate-mp3/music" /etc/samba/smb.conf
add_to_config_text "writeable = yes" /etc/samba/smb.conf
add_to_config_text "browseable = yes" /etc/samba/smb.conf
add_to_config_text "public=no" /etc/samba/smb.conf

pass=123
(echo "$pass"; echo "$pass") | smbpasswd -s -a "$SUDO_USER"