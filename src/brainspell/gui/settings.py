import random

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *


GRID_COLOR = QColor(111,111,111)
GRID_SIZE = 60.0

PLAYER_NUMBER = 8
PLAYER_COLORS = []

for i in range(PLAYER_NUMBER):
    PLAYER_COLORS.append(QColor(\
        random.randint(0,255),\
        random.randint(0,255),\
        random.randint(0,255),\
    ))
ROBOT_IMAGES_NAMES = [
  'alien',
  'angel',
  'basic_guy',
  'billy',
  'borg',
  'bricky',
  'camouflage',
  'candy',
  'chef',
  'cowboy',
  'dandy',
  'devil',
  'fox',
  'geek',
  'geisha',
  'girl',
  'grey',
  'ninja',
  'nurse',
  'pirate',
  'policeman',
  'princess',
  'punker',
  'santa',
  'squared',
  'stripey',
  'sunglasser',
]

random.shuffle(ROBOT_IMAGES_NAMES)

PLAYER_COLORS = zip(PLAYER_COLORS, ROBOT_IMAGES_NAMES)

    