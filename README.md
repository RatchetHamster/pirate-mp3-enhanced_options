# Pirate MP3 - Rev. 2 updates
- Refactor into frontend, core, backend, hardware for easier maintenance. 
- Powersaving option for screen dim
- Screen response upgrade
- Better boot time and sync check time
- Independant button functions on the frontend for easy modifications
- Splash Screen

A quick and dirty MP3 player for Pirate Audio.

You must place your music in the "music" folder and run this package with `python3 -m mp3`.

This fork adds a few enhancements to the UI to expand capability. Some of these enhancements come from audiobook player application (I just wanted a dumb mp3 player that can go in my kids room that they can select books (albums) and chapters (tracks)). 

Case for pirate-audio with speaker and rpi zero 2 w and some funky buttons: https://www.thingiverse.com/thing:6776425

Some settings can be configured in mp3/__init__.py:
1. Sleep time options
2. Default sleep time index
3. long button press duration
4. auto play on startup (True/False)
5. Auto sync music file to a network folder on boot if available. 

## Modifications to pirate-mp3 by RatchetHamster
1. Added resources: default_cover.png; icon-list.png; icon-time-onoff.png
2. Album view: Sleep Icon
3. Album view: list icon instead of return
4. Album view: gap between ablum art
5. Album view: sleep menu (short press); on/off (long press) - top left button
6. Album view: vol +/- persistant volume change and vol indicator
7. Album view: auto play first track album when selected
8. Album view: only draw +/-1 albums for screen (save on processing)
9. Track view: fix view track as current track when go into
10. Track view: persistant scroll (long press) moves in jumps of 2. 
11. Track view: draw only +/- 2 tracks for screen (save on processing)
12. Default Album art when no cover present
13. Auto play on start up (option to turn on and off) by setting "is_playonstartup"
14. Auto play next track and auto switch to next album at end of album
15. Auto Sync to a networked folder (i.e. pull files from a persistant media source)
16. Import Sorted alphabetically for album and track NAMES (not meta title)
17. Pseduo shutdown/sleep; Pseduo wake with button 'A' long press

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
git clone https://github.com/pimoroni/st7789-python
cd st7789-python
./install.sh

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
