import time
from datetime import timedelta
import pathlib
import eyed3
from ST7789 import ST7789
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
from fonts.ttf import RobotoMedium as UserFont
import math
from pygame import mixer
from subprocess import call
import os
from pathlib import Path


# TODO:
# install.sh file - test with clean lite install (backup first)
# Update Git

# Orginal files from: https://github.com/Gadgetoid/pirate-mp3.git
##### Modifications to pirate-mp3 by RatchetHamster
# Added resources: default_cover.png; icon-list.png; icon-time-onoff.png
# Album view: Sleep Icon
# Album view: list icon instead of return
# Album view: gap between ablum art
# Album view: sleep menu (short press); on/off (long press) - top left button
# Album view: vol +/- persistant volume change and vol indicator
# Album view: auto play first track album when selected
# Album view: only draw +/-1 albums for screen (save on processing)
# Track view: fix view track as current track when go into
# Track view: persistant scroll (long press) moves in jumps of 5. 
# Track view: draw only +/- 2 tracks for screen (save on processing)
# Default Album art when no cover present
# Auto play on start up (option to turn on and off) by setting "is_playonstartup"
# Auto play next track - Auto next album
# Auto Sync to a networked folder (i.e. pull files from a persistant media source)
# Import Sorted alphabetically for album and track NAMES (not meta title)
# Pseduo shutdown/sleep; Pseduo wake with button 'A' long press

#region -----USER SETTINGS-----

sleep_times = [None, 1*60*60, 2*60*60, 3*60*60, 4*60*60] # (sec) times that appear in sleep menu
sleep_index = 2   #default index in the sleep times list - set to 0 to turn off by default

long_press_dur = 1 #seconds
is_playonstartup = True # Set to true to autoplay when turned on, false otherwise. 

# Autosync files over network:
is_autosync = False  # setting this to true will make sure the local_rpi_dir is the same as source_dir on a network
local_rpi_dir = "/home/pi/pirate-mp3-enhanced_options/music"
source_dir = "" #eg: //PC/share/dir
source_username = "pi"
source_password = "" #Password for access to network folder

#endregion -------------------

mixer.init()
os.system("amixer set Master 100%")
mixer.music.set_volume(1) #Start at max vol. 

font = ImageFont.truetype(UserFont, 16)

root = pathlib.Path(__file__).parents[0]
resources = root / "resources"

icon_rightarrow = Image.open(resources / "icon-rightarrow.png").convert("RGBA")
icon_backdrop = Image.open(resources / "icon-backdrop.png").convert("RGBA")
icon_return = Image.open(resources / "icon-return.png").convert("RGBA")
icon_play = Image.open(resources / "icon-play.png").convert("RGBA")
icon_stop = Image.open(resources / "icon-stop.png").convert("RGBA")
icon_list = Image.open(resources / "icon-list.png").convert("RGBA")
icon_sleep = Image.open(resources / "icon-time-onoff.png").convert("RGBA")


DISPLAY_W = 240
DISPLAY_H = 240

# The buttons on Pirate Audio are connected to pins 5, 6, 16 and 24
# Boards prior to 23 January 2020 used 5, 6, 16 and 20 
# try changing 24 to 20 if your Y button doesn't work.
BUTTONS = [5, 6, 16, 24]

LABELS = ['A', 'B', 'X', 'Y']


def pseduo_shutdown(backlight, library):
    # using "call(sudo shutdown -h now)" leaves the backlight pin high
    # so even if you turn off screen before shutdown, once pi is haulted 
    # the screen will persist. This stop command is therefore use to turn
    # the screen off and stop all playing audio. 
    # This also allows for a "wake" to be implimented - but the program
    # and pi are still running. 
    global but_press_time
    global persistU_i
    global persistD_i 
    but_press_time={
        "A": None,
        "B": None, 
        "X": None, 
        "Y": None}
    persistU_i = 0 
    persistD_i = 0
    library.stop()
    backlight.ChangeDutyCycle(0) #turn off backlight
    return True

def pseduo_wake(backlight):
    global is_startup
    is_startup = True #maintains auto play or not. 
    backlight.ChangeDutyCycle(100) #turn on backlight
    return False

def icon(image, icon, position, color):
    col = Image.new("RGBA", icon.size, color=color)
    image.paste(col, position, mask=icon)

def text_in_rect(draw, text, font, rect, line_spacing=1.1, textcolor=(0, 0, 0)):
    x1, y1, x2, y2 = rect
    width = x2 - x1
    height = y2 - y1

    # Given a rectangle, reflow and scale text to fit, centred
    while font.size > 0:
        line_height = int(font.size * line_spacing)
        max_lines = math.floor(height / line_height)
        lines = []

        # Determine if text can fit at current scale.
        words = text.split(" ")

        while len(lines) < max_lines and len(words) > 0:
            line = []

            while (
                len(words) > 0
                and font.getsize(" ".join(line + [words[0]]))[0] <= width
            ):
                line.append(words.pop(0))

            lines.append(" ".join(line))

        if len(lines) <= max_lines and len(words) == 0:
            # Solution is found, render the text.
            y = int(
                y1
                + (height / 2)
                - (len(lines) * line_height / 2)
                - (line_height - font.size) / 2
            )

            bounds = [x2, y, x1, y + len(lines) * line_height]

            for line in lines:
                line_width = font.getsize(line)[0]
                x = int(x1 + (width / 2) - (line_width / 2))
                bounds[0] = min(bounds[0], x)
                bounds[2] = max(bounds[2], x + line_width)
                draw.text((x, y), line, font=font, fill=textcolor)
                y += line_height

            return tuple(bounds)

        font = ImageFont.truetype(font.path, font.size - 1)


class Track:
    def __init__(self, path):
        self.path = path
        self.id3 = eyed3.load(path)

    @property
    def title(self):
        return self.id3.tag.title

    def play(self):
        #print(f"Playing {self.path}")
        mixer.music.load(str(self.path))
        mixer.music.play()


class Album:
    def __init__(self, path, cover_art_file):
        self.tracks = []
        self.current_index = 0
        self.playing_index = None
        self.title = path.stem
        self.image = Image.open(cover_art_file).convert("RGB") #removed path / as full path now provided
        self.art = Image.blend(self.image.resize((DISPLAY_W, DISPLAY_H)), Image.new("RGB", (DISPLAY_W, DISPLAY_H), (0, 0, 0)), alpha=0.8)
        self.thumb = self.image.resize((DISPLAY_W // 2, DISPLAY_H // 2))
        source = list(path.glob("*.mp3"))
        source = sorted(source)
        for file in source:
            self.tracks.append(Track(file))

    @property
    def current_track(self):
        return self.tracks[self.current_index]

    @property
    def current_playing_track(self):
        try:
            return self.tracks[self.playing_index]
        except (IndexError, TypeError):
            return None

    def play(self):
        if self.playing_index != self.current_index:
            self.current_track.play()
            self.playing_index = self.current_index
        else:
            self.stop()

    def stop(self):
        self.playing_index = None
        mixer.music.stop()

    def next(self):
        self.current_index += 1
        self.current_index %= len(self.tracks)

    def prev(self):
        self.current_index -= 1
        self.current_index %= len(self.tracks)


class Library:
    def __init__(self, root):
        self.albums = []
        self.current_index = 0

        #Janner Change to include default album art (cover_art_path supplied to album as full path not fname): 
        allfold = sorted(os.scandir(root), key=lambda e: e.name)
        subfolders = [ Path(f.path) for f in allfold if f.is_dir() ]
        for file in subfolders:
            if os.path.exists(os.path.join(file,'cover.png')):
                cover_art_path = os.path.join(file,'cover.png')
            elif os.path.exists(os.path.join(file,'cover.jpg')):
                cover_art_path = os.path.join(file,'cover.jpg')
            else:
                cover_art_path = os.path.join(str(Path(*root.parts[0:-1])), 'mp3', 'resources', 'default_cover.png')
            self.albums.append(Album(file, cover_art_path))

    @property
    def current_album(self):
        return self.albums[self.current_index]

    def next(self):
        self.current_index += 1
        self.current_index %= len(self.albums)

    def prev(self):
        self.current_index -= 1
        self.current_index %= len(self.albums)

    def play(self):
        for album in self.albums:
            album.stop()
        self.current_album.play()

    def stop(self):
        self.current_album.stop()

view = "album"

sleep_start_time = time.time()
persistU_i = 0 
persistD_i = 0

is_shutdown = False
is_startup = True

but_press_time={
        "A": None,
        "B": None, 
        "X": None, 
        "Y": None}

def main():
    global view     #way too many globals!! haha
    global sleep_index
    global sleep_start_time
    global persistD_i
    global persistU_i
    global is_shutdown
    global is_startup
    global is_playonstartup
    global but_press_time

    ### File Sync Section - This can take time on boot
    if is_autosync:
        os.system(f'sudo mount {source_dir} /mnt/ -o username={source_username},password={source_password}') # Mount source - may require username and password
        os.system(f'rsync -r /mnt/ {local_rpi_dir}')
        os.system(f'sudo umount /mnt/')
    ###

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Backlight:
    GPIO.setup(13, GPIO.OUT)
    backlight = GPIO.PWM(13, 500)
    backlight.start(100) # start at 100%

    display = ST7789(
        rotation=90,
        port=0,
        cs=1,
        dc=9,
        backlight=None, #Modified as we will control this on shutdown
        spi_speed_hz=80 * 1000 * 1000
    )

    canvas = Image.new("RGB", (DISPLAY_W, DISPLAY_H), (0, 0, 0))

    music_path = root.parents[0] / "music"
    print(f"Loading music from {music_path}")
    library = Library(music_path)

    def handle_button(pin):
        global view
        global sleep_index
        global sleep_start_time
        global is_shutdown
        global persistU_i
        global persistD_i
        label = LABELS[BUTTONS.index(pin)]

        if is_shutdown and label!="A":
            # Disable other buttons if shutdown
            return

        if but_press_time[label]==None: # Button press:
            but_press_time[label] = time.time()
            return

        # Button release:
        
        if view == "album":
            if label == "A":
                if time.time()-but_press_time[label] > long_press_dur:
                    if is_shutdown: 
                        is_shutdown = pseduo_wake(backlight)
                    else:
                        is_shutdown = pseduo_shutdown(backlight, library)
                else:
                    sleep_index = (sleep_index+1)%len(sleep_times)
                    sleep_start_time = time.time()
            if label == "B":
                if time.time()-but_press_time[label] < long_press_dur: # short press  
                    library.prev()
                    library.play()
                persistD_i = 0
            if label == "Y":
                if time.time()-but_press_time[label] < long_press_dur: #short press    
                    library.next()
                    library.play()
                persistU_i = 0
            if label == "X":
                view = "track"
                if library.current_album.playing_index!=None:
                    library.current_album.current_index=library.current_album.playing_index+1
                else:
                    library.current_album.current_index=1
        if view == "track":
            if label == "A":
                view = "album"
            if label == "B":
                if mixer.music.get_busy() and library.current_album.current_track == library.current_album.current_playing_track:
                    library.stop()
                else:
                    library.play()
            if label == "X":
                library.current_album.prev()
                persistU_i = 0
            if label == "Y":
                library.current_album.next()
                persistD_i = 0
        
        but_press_time[label] = None # cleanup

    for pin in BUTTONS:
        GPIO.add_event_detect(pin, GPIO.BOTH, handle_button, bouncetime=50)


    while True:
        if is_startup==is_playonstartup:
            library.play()
            sleep_start_time = time.time()
            is_startup = False

        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, DISPLAY_W, DISPLAY_H), (0, 0, 0))

        selected_album = library.current_index

        if library.albums[selected_album].playing_index!= None and not mixer.music.get_busy(): #auto play next track
            if library.albums[selected_album].playing_index==len(library.albums[selected_album].tracks)-1: #if end of album
                view="ablum"
                library.next()
                library.play()
            else:
                library.albums[selected_album].next()
                library.albums[selected_album].play()

        if view == "album":

            # Persistant volume control: 
            time_vol_inc = 0.5 #seconds
            if but_press_time["B"]!=None: 
                if time.time()-but_press_time["B"]-long_press_dur-time_vol_inc*(persistD_i+1)>time_vol_inc:
                    persistD_i+=1
                    mixer.music.set_volume(mixer.music.get_volume()-0.05)
            if but_press_time["Y"]!=None: 
                if time.time()-but_press_time["Y"]-long_press_dur-time_vol_inc*(persistU_i+1)>time_vol_inc:
                    persistU_i+=1
                    mixer.music.set_volume(mixer.music.get_volume()+0.05)

            offset_x = (DISPLAY_W // 4) - ((DISPLAY_W // 2 +20) * selected_album)
            
            from_album = selected_album-1
            if from_album<0:
                from_album = selected_album
            to_album = selected_album + 2
            if to_album>len(library.albums):
                to_album = selected_album+1

            for i in range(from_album,to_album):
                album = library.albums[i]
                canvas.paste(album.thumb, (offset_x + (140 * i), 60), None)

            text_in_rect(draw, library.current_album.title, font, (26, DISPLAY_H - 60, DISPLAY_W - 26, DISPLAY_H), line_spacing=1.1, textcolor=(255, 255, 255))

            icon(canvas, icon_backdrop, (0, 47), (255, 255, 255))
            icon(canvas, icon_sleep, (0, 50), (0, 0, 0))
            
            icon(canvas, icon_backdrop.rotate(180), (DISPLAY_W - 26, 47), (255, 255, 255))
            icon(canvas, icon_list.rotate(0), (DISPLAY_W - 20, 50), (0, 0, 0))

            icon(canvas, icon_backdrop, (0, DISPLAY_H - 73), (255, 255, 255))
            icon(canvas, icon_rightarrow.rotate(180), (0, DISPLAY_H - 70), (0, 0, 0))

            icon(canvas, icon_backdrop.rotate(180), (DISPLAY_W - 26, DISPLAY_H - 73), (255, 255, 255))
            icon(canvas, icon_rightarrow, (DISPLAY_W - 20, DISPLAY_H - 70), (0, 0, 0))

            # Sleep time: 
            if sleep_times[sleep_index] != None:
                time_to_sleep = sleep_times[sleep_index] - (time.time() - sleep_start_time)
                if time_to_sleep < 0:
                    is_shutdown = pseduo_shutdown(backlight, library)
                text_in_rect(draw, f'Sleep: {str(timedelta(seconds=round(time_to_sleep)))}', font, (26, 0, DISPLAY_W - 26, 60), line_spacing=1.1, textcolor=(255, 255, 255))

            # Volume: 
            text_in_rect(draw, f'{round(mixer.music.get_volume()*100)}%', font, (0, 0, 45, 30), line_spacing=1.1, textcolor=(255, 255, 255))

        elif view == "track":
            # Persistant scroll control: 
            time_scroll_inc = 0.7 #seconds
            skip_per_scroll = 2
            if but_press_time["X"]!=None: 
                if time.time()-but_press_time["X"]-long_press_dur-time_scroll_inc*(persistU_i+1)>time_scroll_inc:
                    persistU_i+=1
                    for _ in range(skip_per_scroll):
                        library.current_album.prev()
            if but_press_time["Y"]!=None: 
                if time.time()-but_press_time["Y"]-long_press_dur-time_vol_inc*(persistD_i+1)>time_vol_inc:
                    persistU_i+=1
                    for _ in range(skip_per_scroll):
                        library.current_album.next()
                    
            album = library.current_album

            selected_track = album.current_index

            canvas.paste(album.art, (0, 0), None)

            item = 0
            offset_y = (DISPLAY_H // 2) - 2.5*24

            #offset_y -= selected_track * 24

            track_overlay = Image.new("RGBA", (DISPLAY_W, DISPLAY_H))
            track_draw = ImageDraw.Draw(track_overlay)

            if selected_track-2<0:
                from_track=0
            else:
                from_track = selected_track-2
            if from_track+5>len(album.tracks):
                to_track = len(album.tracks)
                if to_track - 5<0:
                    from_track=0
                else: 
                    from_track = to_track-5
            else:
                to_track = from_track+5

            for t in range(from_track, to_track):
                track = album.tracks[t]
                position_y = offset_y + item * 24
                track_draw.rectangle((0, position_y, DISPLAY_W, position_y + 24), fill=(0, 0, 0, 200) if item % 2 else (0, 0, 0, 180))

                if track == album.current_playing_track:
                    track_draw.text((55, 1 + position_y), track.title, font=font, fill=(255, 255, 255))
                elif track == album.current_track:
                    track_draw.text((55, 1 + position_y), track.title, font=font, fill=(200, 200, 200))
                else:
                    track_draw.text((55, 1 + position_y), track.title, font=font, fill=(64, 64, 64))
                item += 1

            canvas = Image.alpha_composite(canvas.convert("RGBA"), track_overlay)

            text_in_rect(draw, album.title, font, (0, 0, DISPLAY_W, 30), line_spacing=1.1, textcolor=(255, 255, 255))

            icon(canvas, icon_backdrop, (0, 47), (255, 255, 255))
            icon(canvas, icon_return, (0, 53), (0, 0, 0))

            icon(canvas, icon_backdrop.rotate(180), (DISPLAY_W - 26, 47), (255, 255, 255))
            icon(canvas, icon_rightarrow.rotate(90), (DISPLAY_W - 20, 50), (0, 0, 0))

            icon(canvas, icon_backdrop.rotate(180), (DISPLAY_W - 26, DISPLAY_H - 73), (255, 255, 255))
            icon(canvas, icon_rightarrow.rotate(-90), (DISPLAY_W - 20, DISPLAY_H - 70), (0, 0, 0))

            # Play/Pause
            icon(canvas, icon_backdrop, (0, DISPLAY_H - 73), (255, 255, 255))
            if mixer.music.get_busy() and album.current_track == album.current_playing_track:
                icon(canvas, icon_stop, (0, DISPLAY_H - 70), (0, 0, 0))
            else:
                icon(canvas, icon_play, (0, DISPLAY_H - 70), (0, 0, 0))


        display.display(canvas)
        #time.sleep(1.0 / 20)

    return 1
