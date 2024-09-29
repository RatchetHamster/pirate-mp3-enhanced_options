import os
import eyed3
import pathlib
from PIL import Image
from random import randint
from mp3.hardware import DISPLAY_W, DISPLAY_H
from pathlib import Path
from mp3.core import Core


RESOURCES = pathlib.Path(__file__).resolve().parent / "resources"


class Track:
    """Properties:
        path (str): path to mp3
        id3 (eyed3): eyed3 object of mp3
        title (str): displayed in Track view
    """

    def __init__(self, path):
        self.path = path
        print(f'Loading: {path}')
        self.id3 = eyed3.load(path)

    @property
    def title(self):
        # If not title tag, default to fname
        if self.id3.tag==None or self.id3.tag.title == None: 
            return self.path.stem[:-4]
        return self.id3.tag.title

    def play(self):
        Core().load(str(self.path))
        Core().play()


class Album:
    """Properties:
        tracks (list): List of track objects in the ablum
        current_index (int): 0 origin index of track "selected" in "tracks"
        playing_index (int): 0 origin index of track playing in "track" - None if stopped
        title (str): title meta data, or if none exists, fname stripped of extension
        image (Image): unmodded image of cover art
        art (Image): darken image that fills screen (for background of "track view")
        thumb (Image): half disp image for "ablum view"
        current_track (Track): Track object selected
        current_playing_Track (Track): Track objects of playing track (None if stopped)
    """

    def __init__(self, path, cover_art_file):
        self.tracks = []
        self.current_index = 0
        self.playing_index = None
        self.title = path.stem
        self.image = Image.open(cover_art_file).convert("RGB")
        self.art = Image.blend(self.image.resize((DISPLAY_W, DISPLAY_H)), Image.new("RGB", (DISPLAY_W, DISPLAY_H), (0, 0, 0)), alpha=0.8)
        self.thumb = self.image.resize((DISPLAY_W // 2, DISPLAY_H // 2))
        source = list(path.glob("*.mp3"))
        for file in sorted(source):
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
        Core().stop()

    def next(self):
        self.current_index += 1
        self.current_index %= len(self.tracks)

    def prev(self):
        self.current_index -= 1
        self.current_index %= len(self.tracks)      


class Library:
    def __init__(self, root):
        self.root = root

    def setup(self, pick_random_album=False):
        self.view = "album"
        self.albums = []
        self.current_index = 0
        allfold = sorted(os.scandir(self.root), key=lambda e: e.name)
        subfolders = [ Path(f.path) for f in allfold if f.is_dir() ]
        for file in subfolders:
            if os.path.exists(os.path.join(file,'cover.png')):
                cover_art_path = os.path.join(file,'cover.png')
            elif os.path.exists(os.path.join(file,'cover.jpg')):
                cover_art_path = os.path.join(file,'cover.jpg')
            else:
                cover_art_path = os.path.join(str(Path(*self.root.parts[0:-1])), 'mp3', 'resources', 'default_cover.png')
            self.albums.append(Album(file, cover_art_path))
        
        if pick_random_album:
            self.current_index = randint(0,len(self.albums))

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
    
    def inc_vol(self, inc):
        Core().inc_vol(inc)
    
    def is_busy(self):
        return Core().is_busy()
    
    def get_vol(self):
        return Core().get_vol()

    def auto_next(self, auto_track_next=True, auto_album_next=True):
        if auto_track_next:
            if self.albums[self.current_index].playing_index!= None and not Core().is_busy(): #auto play next track
                if self.albums[self.current_index].playing_index==len(self.albums[self.current_index].tracks)-1: #if end of album
                    if auto_album_next:
                        self.view="ablum"
                        self.next()
                    else:
                        self.albums[self.current_index].next()
                else:
                    self.albums[self.current_index].next()
                self.play()

