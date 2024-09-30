import math
import os
import time
from PIL import Image, ImageFont, ImageDraw
from fonts.ttf import RobotoMedium as UserFont
from datetime import timedelta
from mp3.backend import RESOURCES
from mp3.hardware import Board


#region ----- Network Sync Settings -----

is_autosync = False  # setting this to true will make sure the local_rpi_dir is the same as source_dir on a network
local_rpi_dir = ""
source_dir = ""
source_username = ""
source_password = ""

#endregion -------------------


#region ----- Fonts and Resources -----

font = ImageFont.truetype(UserFont, 16)

icon_rightarrow = Image.open(RESOURCES / "icon-rightarrow.png").convert("RGBA")
icon_backdrop = Image.open(RESOURCES / "icon-backdrop.png").convert("RGBA")
icon_return = Image.open(RESOURCES / "icon-return.png").convert("RGBA")
icon_play = Image.open(RESOURCES / "icon-play.png").convert("RGBA")
icon_stop = Image.open(RESOURCES / "icon-stop.png").convert("RGBA")
icon_list = Image.open(RESOURCES / "icon-list.png").convert("RGBA")
icon_sleep = Image.open(RESOURCES / "icon-time-onoff.png").convert("RGBA")
splash = Image.open(RESOURCES / "splash.png").convert("RGBA")

#endregion


#region ----- Functions -----

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

#endregion


#region ----- Classes ----- 

class Frontend():
    def __init__(self, library):
        self.library = library
        self.board = Board(self)

        #Configureable:
        self.sleep_times = [None, 1*60*60, 2*60*60, 3*60*60, 4*60*60] # (sec) times that appear in sleep menu
        self.sleep_index = 3   #default index in the sleep times list - set to 0 to turn off by default
        self.is_playonstartup = True # Set to true to autoplay when turned on, false otherwise. 
        self.start_at_random_album = True #if true, pick random album
        self.num_track_skip_per_scroll = 2
        self.persist_inc_time = 0.3 #(sec)

        self.is_enable_powersave = True
        self.powersave_dur = 10 #(sec)
        self.normal_sleep_percyc = 0.1
        self.powersave_sleep_percyc = 1
        self.is_powersave = False

        self.persist_i = {
            "A": 0,
            "B": 0, 
            "X": 0, 
            "Y": 0}
        self.canvas = Image.new("RGB", (self.board.DISPLAY_W, self.board.DISPLAY_H), (0, 0, 0))
        self.display_splash()

        # Autosync:
        if is_autosync:
            os.system(f'sudo mount {source_dir} /mnt/ -o username={source_username},password={source_password}') # Mount source - may require username and password
            os.system(f'rsync --recursive --ignore-existing --delete -P /mnt/ {local_rpi_dir}')
            os.system(f'sudo umount /mnt/')
        
        # Startup actions:
        self.library.setup(self.start_at_random_album)
        self.startup_play()
        self.board.time_of_last_but_press = time.time()
        self.sleep_start_time = time.time()

    def startup_play(self):
        if self.is_playonstartup:
            self.library.play()

    #region Button Calls:
    def buttonA_pressed(self):
        self.wake_from_idle()

    def buttonB_pressed(self):
        self.wake_from_idle()

    def buttonX_pressed(self):
        self.wake_from_idle()

    def buttonY_pressed(self):
        self.wake_from_idle()

    def buttonA_held(self):
        pass

    def buttonB_held(self):
        if self.library.view == "album":
            self.library.inc_vol(-0.05)

    def buttonX_held(self):
        if self.library.view == "track":
            for _ in range(self.num_track_skip_per_scroll):
                self.library.current_album.prev()

    def buttonY_held(self):
        if self.library.view == "album":
            self.library.inc_vol(0.05)
        elif self.library.view == "track":
            for _ in range(self.num_track_skip_per_scroll):
                self.library.current_album.next()

    def buttonA_released(self, press_duration):
        if self.library.view == "album":
            if press_duration > self.board.long_press_dur: #Long Press
                if self.board.is_shutdown: 
                    self.board.pseduo_wake()
                    self.sleep_start_time = time.time()
                else:
                    self.board.pseduo_shutdown()
            else: # Short Press
                self.sleep_index = (self.sleep_index+1)%len(self.sleep_times)
                self.sleep_start_time = time.time()
        elif self.library.view == "track":
            self.library.view = "album"
        self.persist_i["A"]=0

    def buttonB_released(self, press_duration):
        if self.library.view == "album":
            if press_duration < self.board.long_press_dur: # short press  
                self.library.prev()
                self.library.play()
            self.persist_i["B"] = 0
        if self.library.view == "track":
            if self.library.is_busy() and self.library.current_album.current_track == self.library.current_album.current_playing_track:
                self.library.stop()
            else:
                self.library.play()
        self.persist_i["B"]=0

    def buttonY_released(self, press_duration):
        if self.library.view == "album":
            if press_duration < self.board.long_press_dur: #short press    
                self.library.next()
                self.library.play()
        if self.library.view == "track":    
            self.library.current_album.next()
        self.persist_i["Y"]=0

    def buttonX_released(self, press_duration):
        if self.library.view == "album":    
            self.library.view = "track"
            if self.library.current_album.playing_index!=None:
                self.library.current_album.current_index=self.library.current_album.playing_index
            else:
                self.library.current_album.current_index=0
        elif self.library.view == "track":
            self.library.current_album.prev()
        self.persist_i["X"]=0
    #endregion

    #region Sleep and Idle Checks:
    def get_sleep_time_left(self):
        if self.sleep_times[self.sleep_index] != None:
            return self.sleep_times[self.sleep_index] - (time.time() - self.sleep_start_time)
        return None

    def check_sleep_idle(self):
        if not self.board.is_shutdown:
            if self.sleep_times[self.sleep_index] != None:
                if self.get_sleep_time_left() < 0:
                    self.board.pseduo_shutdown()
        if self.is_enable_powersave and not self.board.is_shutdown:
            if (time.time() - self.board.time_of_last_but_press) > self.powersave_dur:
                self.board.screen_dim()
                self.is_powersave = True

    def wake_from_idle(self):
        if self.is_powersave:
            self.is_powersave = False
            self.board.screen_on()
    #endregion

    #region Drawing
    def update_frame(self):
        if not self.board.is_shutdown:
            view = self.library.view

            # Persistant Function call:
            for label in self.board.LABELS:
                if self.board.but_press_time[label]!=None:
                    tot_press_dur = time.time()-self.board.but_press_time[label]
                    time_since_last_persist_inc = tot_press_dur - self.board.long_press_dur - self.persist_inc_time * (self.persist_i[label])
                    if time_since_last_persist_inc>0: 
                        self.persist_i[label]+=1
                        self.board.held_functions[label]()
            
            self.draw = ImageDraw.Draw(self.canvas)
            self.draw.rectangle((0, 0, self.board.DISPLAY_W, self.board.DISPLAY_H), (0, 0, 0))

            if view == "album":
                self.album_view_create()

            elif view == "track":
                self.track_view_create()

            self.board.display.display(self.canvas)

        if self.is_powersave or self.board.is_shutdown:
            time.sleep(self.powersave_sleep_percyc)
        else:
            time.sleep(self.normal_sleep_percyc)
    
    def album_view_create(self):
        DISPLAY_W = self.board.DISPLAY_W
        DISPLAY_H = self.board.DISPLAY_H
        selected_album = self.library.current_index
        offset_x = (DISPLAY_W // 4) - ((DISPLAY_W // 2 +20) * selected_album)
            
        from_album = selected_album-1
        if from_album<0:
            from_album = selected_album
        to_album = selected_album + 2
        if to_album>len(self.library.albums):
            to_album = selected_album+1

        for i in range(from_album,to_album):
            album = self.library.albums[i]
            self.canvas.paste(album.thumb, (offset_x + (140 * i), 60), None)

        text_in_rect(self.draw, self.library.current_album.title, font, (26, DISPLAY_H - 60, DISPLAY_W - 26, DISPLAY_H), line_spacing=1.1, textcolor=(255, 255, 255))

        self.draw_icons(icon_sleep, icon_rightarrow.rotate(180), icon_list, icon_rightarrow)

        # Sleep time:   
        if self.get_sleep_time_left() != None:
            text_in_rect(self.draw, f'Sleep: {str(timedelta(seconds=round(self.get_sleep_time_left())))}', font, (26, 0, DISPLAY_W - 26, 60), line_spacing=1.1, textcolor=(255, 255, 255))

        # Volume: 
        text_in_rect(self.draw, f'{round(self.library.get_vol()*100)}%', font, (0, 0, 45, 30), line_spacing=1.1, textcolor=(255, 255, 255))

    def track_view_create(self):
        DISPLAY_W = self.board.DISPLAY_W
        DISPLAY_H = self.board.DISPLAY_H

        album = self.library.current_album
        selected_track = album.current_index
        self.canvas.paste(album.art, (0, 0), None)

        item = 0
        offset_y = (DISPLAY_H // 2) - 2.5*24

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

        self.canvas = Image.alpha_composite(self.canvas.convert("RGBA"), track_overlay)

        text_in_rect(self.draw, album.title, font, (0, 0, DISPLAY_W, 30), line_spacing=1.1, textcolor=(255, 255, 255))

        icon_playpause = icon_play
        if self.library.is_busy() and album.current_track == album.current_playing_track:
            icon_playpause = icon_stop
        self.draw_icons(icon_return, icon_playpause, icon_rightarrow.rotate(90), icon_rightarrow.rotate(-90))
            
    def draw_icons(self, iconA, iconB, iconX, iconY):
        #Backdrops:
        icon(self.canvas, icon_backdrop, (0, 47), (255, 255, 255))
        icon(self.canvas, icon_backdrop.rotate(180), (self.board.DISPLAY_W - 26, 47), (255, 255, 255))
        icon(self.canvas, icon_backdrop, (0, self.board.DISPLAY_H - 73), (255, 255, 255))
        icon(self.canvas, icon_backdrop.rotate(180), (self.board.DISPLAY_W - 26, self.board.DISPLAY_H - 73), (255, 255, 255))
        #Icons:
        icon(self.canvas, iconA, (0, 50), (0, 0, 0))
        icon(self.canvas, iconB, (0, self.board.DISPLAY_H - 70), (0, 0, 0))
        icon(self.canvas, iconX.rotate(0), (self.board.DISPLAY_W - 20, 50), (0, 0, 0))
        icon(self.canvas, iconY, (self.board.DISPLAY_W - 20, self.board.DISPLAY_H - 70), (0, 0, 0))

    def display_splash(self):
        self.canvas.paste(splash, (0, 0), None)
        self.board.display.display(self.canvas)
#endregion
