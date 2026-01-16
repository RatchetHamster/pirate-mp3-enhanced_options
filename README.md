# Pirate MP3 - Rev. 2 updates
- Refactor into frontend, core, backend, hardware for easier maintenance. 
- Powersaving option for screen dim
- Screen response upgrade
- Better boot time and sync check time
- Independant button functions on the frontend for easy modifications
- Splash Screen

A quick and dirty MP3 player for Pirate Audio.

You must place your music in the "music" folder.

Case for pirate-audio with speaker and rpi zero 2 w and some funky buttons: https://www.thingiverse.com/thing:6776425

## To upgrate from git  
cd /home/pi/pirate-mp3-ehnaced_options
git pull
sudo reboot

## To Install
SSH into fresh install  
sudo apt update
sudo apt upgrade -y
sudo apt install git -y  
git clone this repo  

# Samba: 
sudo apt update && sudo apt upgrade -y && sudo apt install samba samba-common-bin -y  
sudo nano /etc/samba/smb.conf  
Add to the end of the file for each share:  

[pirateMP3]  
path = /home/pi/pirate-mp3-enhanced_options/music  
writeable = yes  
browseable = yes  
public=no  

Setup samba password and user:  
sudo smbpasswd -a pi  
enter password  
setup network folder on windows machine  

# Config
Modify /boot/fireware/config.txt (get sound working on Pirate-Audio)  
sudo nano /boot/firmware/config.txt  
add to line 5:  
dtoverlay=hifiberry-dac
gpio=25=op,dh

sudo raspi-confi
enable i2c and spi

# User Groups:  
usermod -a -G spi,i2c,gpio,video,audio pi  

# SETUP PYTHON VENV
python -m venv /home/pi/venv/  
source /home/pi/venv/bin/activate  
pip install -r /home/pi/python/pirate-mp3-enhanced_options/mp3/requirements.txt  
sudo apt update  
sudo apt install python3.13-dev  
git clone https://github.com/pimoroni/st7789-python  
cd st7789-python  
./install.sh  
pip install https://github.com/Gadgetoid/PY_LGPIO/releases/download/0.2.2.0/lgpio-0.2.2.0.tar.gz  
Requirements should install ok, there is some pain around st7789 libraries and the lgpio used as a pin library in gpiozero, hopefully this should work  

# Service
Move .service file to correct location  
sudo mv /home/pi/pirate-mp3-enhanced_options/mp3/pirate-mp3.service /etc/systemd/system/  

#Enable service at boot  
sudo systemctl daemon-reload && sudo systemctl enable pirate-mp3 && sudo systemctl start pirate-mp3  

#Create logrotate limit on log file  
sudo nano /etc/logrotate.d/pirate-mp3  
into the file put:  
/var/log/pirate-mp3.log  
{  
weekly  
minsize 1M  
maxsize 10M  
rotate 4  
missingok  
notifempty    
}  

-------------------

## Adding Music  

Music must be in mp3 format, arranged into subfolders and include a `cover.jpg` or `cover.png` album art file. If the folder does not include cover art, it will use the crappy default. 
Suimilar can be done for audiobooks - each folder is the book with track chapters inside. cover.jpg adn cover.png still apply (it still sees them as albums). 

EG:

```
music/
├── Sabrepulse - Exile
│   ├── cover.png
│   ├── Sabrepulse - Exile - 01 The Artist & The Engineer.mp3
│   ├── Sabrepulse - Exile - 02 Further To Etherworld.mp3
│   ├── Sabrepulse - Exile - 03 Familiar.mp3
│   ├── Sabrepulse - Exile - 04 Banish.mp3
│   ├── Sabrepulse - Exile - 05 Hayati.mp3
│   ├── Sabrepulse - Exile - 06 Exit Berlin.mp3
│   ├── Sabrepulse - Exile - 07 1985.mp3
│   └── Sabrepulse - Exile - 08 In The End We Are All Cosmic.mp3
├── Sabrepulse - First Crush
│   ├── cover.png
│   ├── Sabrepulse - First Crush - 01 First Crush (Featuring Knife City).mp3
│   ├── Sabrepulse - First Crush - 02 The Advantage (Featuring Henry Homesweet).mp3
│   ├── Sabrepulse - First Crush - 03 City At Speed.mp3
│   ├── Sabrepulse - First Crush - 04 Arcanine.mp3
│   ├── Sabrepulse - First Crush - 05 Paradise.mp3
│   ├── Sabrepulse - First Crush - 06 The Rapture.mp3
│   ├── Sabrepulse - First Crush - 07 Futureproof.mp3
│   └── Sabrepulse - First Crush - 08 We Were Young.mp3
```
