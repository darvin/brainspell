import os
import sys

def trydir(dirname, filename):
    f_dev = os.path.join(dirname,filename)
    if os.path.isfile(f_dev) or os.path.isdir(f_dev):
        return f_dev
    else:
        return None
    
def resfile(filename):
    dirs = []
    dirs += [os.path.join(os.path.dirname(__file__),'..','..','..','resources')]
    dirs += [os.path.join(os.path.dirname(__file__),'..','..')]
    
    dirs += [os.path.join(sys.prefix, 'share', 'brainspell')]
    
    for d in dirs:
        if trydir(d,filename) is not None:
            return trydir(d,filename)
    
MUSIC_LIST = [
'a-dark-and-desperate-intro.ogg',
'alien_ruins2.ogg',
'amigawasbetter3.ogg',
'extremebinarydrumandbass.ogg',
'mechanicalchoir3.ogg',
'pacman background music.ogg',
]
SOUNDS = {
    "robot_create": "robot_create.ogg",
    "robot_walk": "walk.ogg",
    "robot_trap": "trap.ogg",
}
