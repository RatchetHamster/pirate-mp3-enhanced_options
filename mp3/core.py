import os
from pygame import mixer


class Core():        
    
    def setup(self):
        mixer.init()
        os.system("amixer set Master 100%")
        mixer.music.set_volume(0.4) #Start at max vol
    
    def load(self, path_str):
        mixer.music.load(path_str)
    
    def play(self):
        mixer.music.play()
    
    def stop(self):
        mixer.music.stop()
    
    def is_busy(self):
        return mixer.music.get_busy()
    
    def inc_vol(self, amount):
        mixer.music.set_volume(mixer.music.get_volume()+amount)
    
    def get_vol(self):
        return mixer.music.get_volume()
