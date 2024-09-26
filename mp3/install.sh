#!/bin/bash

# To install run: 
# [You may need to install pip install git if lite version of rasbian]
# git clone https://github.com/RatchetHamster/pirate-mp3-enhanced_options.git
# /home/pi/pirate-mp3-enhanced_options/install.sh

# Update and upgrade
sudo apt update
sudo apt upgrade

# Create, activate and install packages on virtural python env. 
python3 -m venv /home/pi/pirate-mp3-enhanced_options/venv
source /home/pi/pirate-mp3-enhanced_options/venv/bin/activate
pip install -r /home/pi/pirate-mp3-enhanced_options/mp3/requirements.txt

# Modify /boot/fireware/config.txt (get sound working on Pirate-Audio)
function add_to_config_text {
    CONFIG_LINE="$1"
    CONFIG="$2"
    LINE_NUMBER="$3"
    sed -i "/$CONFIG_LINE/d" $CONFIG
    sed -i "${LINE_NUMBER}i ${CONFIG_LINE}" $CONFIG
}
add_to_config_text "gpio=25=op,dh" /boot/firmware/config.txt 5
add_to_config_text "dtoverlay=hifiberry-dac" /boot/firmware/config.txt 5

# Run on boot (modify /etc/rc.local so that module runs on boot)
# check: /tmp/rc.local.log for errors, warnings and outputs
add_to_config_text 'su --command "PYTHONPATH=\/home\/pi\/pirate-mp3-enhanced_options \/home\/pi\/pirate-mp3-enhanced_options\/venv\/bin\/python3 -m mp3" --login pi' /etc/rc.local 19
add_to_config_text "set -x" /etc/rc.local 19
add_to_config_text "exec 1>&2" /etc/rc.local 19
add_to_config_text "exec 2> \/tmp\/rc.local.log" /etc/rc.local 19
