# Pirate MP3

A quick and dirty MP3 player for Pirate Audio.

You must place your music in the "music" folder and run this package with `python3 -m mp3`.

This fork adds a few enhancements to the UI to expand capability. Some of these enhancements come from audiobook player application (I just wanted a dumb mp3 player that can go in my kids room that they can select books (albums) and chapters (tracks)). 

Case for pirate-audio with speaker and rpi zero 2 w and some funky buttons: https://www.thingiverse.com/thing:6776425

## Changes in this fork: 
1. Added to resources: default_cover.png; icon-list.png; icon-time-onoff.png
2. Album view: Sleep icon on button A
3. Album view: list icon instead of return icon for button X
4. Album view: gap between album art
5. Album view: Button A - Sleep menu and display (short press); sleep/wake (long press)
6. Album view: "pseduo shutdown" and "pseduo wake" (long press button A) - does not actually shutdown pi or even end program, just turns of screen and shuts it up. 
7. Album view: Vol +/- (persistant long press buttons B & Y) and volume % indicator
8. Album view: autoplay first track in album when switching (i.e. short press B & Y starts playing new album (book)
9. Default Album art when none present in folder. 
10. Track view: fix view track as the "current track" when entering track view
11. Track view: (persistant long press buttons X & Y) moves in 5 track jumps
12. Auto play on startup (i.e. first track of first album plays) - can be toggled by setting "is_playonstartup" to False in __init__.py

## Requirements

TO BE COMPLETED STILL!!!!
To Do: 
1. write code to run in SSH, something like: git clone this repo; run install.sh - that should be all - don't know yet. 
2. write requirements.txt file for virtual enviroment install (pillow must be 9.5.0 not later - pip install "Pillow=9.5.0")
3. write install.sh to handle setup:
4. install.sh needs to: 
* add "dtoverlay=hifberry-dac" and "gpio=25=op,dh" to /boot/firmware/config.txt
* set alsamix vol to max
* add on boot stuff to rc.local - not yet figured out!

```
python3 -m pip install eyed3
```

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
