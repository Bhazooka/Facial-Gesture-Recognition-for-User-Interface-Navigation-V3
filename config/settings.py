from datetime import datetime

# CAMERA = 1 # Usually 0, depends on input device(s)
CAMERA = 0

# Optionally record the video feed to a timestamped AVI in the current directory
RECORDING = False
FPS = 10
RECORDING_FILENAME = str(datetime.now()).replace('.','').replace(':','') + '.avi'

FACE_TILT = .5

EYE_BLINK_HEIGHT = .15
EYE_SQUINT_HEIGHT = .18
EYE_OPEN_HEIGHT = .25
EYE_BUGGED_HEIGHT = .7

MOUTH_OPEN_HEIGHT = .2
MOUTH_OPEN_SHORT_FRAMES = 1
MOUTH_OPEN_LONG_FRAMES = 4
MOUTH_CLOSED_FRAMES = 1

MOUTH_FROWN = .006
MOUTH_NOSE_SCRUNCH = .09
MOUTH_SNARL = .1
MOUTH_DUCKFACE = 1.6

BROW_RAISE_LEFT = .0028
BROW_RAISE_RIGHT = .025
BROWS_RAISE = .19

WAIT_FRAMES = 6