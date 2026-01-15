from backend import Library
from frontend import Frontend
from core import Core

#region Main

def main():
    Core().setup()
    AUDIO = "/home/pi/pirate-mp3-enhanced_options/music"
    library = Library(AUDIO)
    frontend = Frontend(library)
    
    while True:
        library.auto_next(auto_track_next=True, auto_album_next=True)
        frontend.update_frame()
        frontend.check_sleep_idle()

main()

#endregion
