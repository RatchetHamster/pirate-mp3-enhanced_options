I am in the process of verofying the install.sh and samba_setup.sh - completed soon

# Pirate MP3

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

## Requirements

Run this code on fresh install of Rasbian: 
(need to run 'sudo apt install git' if lite version of Rasbian)
```
git clone https://github.com/RatchetHamster/pirate-mp3-enhanced_options.git
/home/pi/pirate-mp3/mp3/install.sh
```
The install file does the following:
1. Update upgrade
2. Python virtual env setup, activate and install mp3/requirements.txt
3. Modify /boot/firmware/config.txt file to get audio working
4. Modify /etc/rc.local to start module on boot and log output to /tmp/rc.local.log
(optionally):
5. sudo nano /home/pi/pirate-mp3/mp3/samba_setup.sh
6. enter password for network share; crtl+x; y; enter
7. /home/pi/pirate-MP3/mp3/samba_setup.sh

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

## Samba network folder

This player becomes very powerful if you have wifi setup and create a networked folder on the /home/pi/pirate-mp3/music folder so that you can add/remove music from a windows device. I use this tutorial:
https://pimylifeup.com/raspberry-pi-samba/

Although, where it asks you to create a new folder - you just use the one that is already there. 
