import cv2
from scipy.spatial import distance as dist
import keyboard
from config.settings import (
    FACE_TILT, EYE_BLINK_HEIGHT, EYE_SQUINT_HEIGHT, EYE_OPEN_HEIGHT, EYE_BUGGED_HEIGHT,
    MOUTH_OPEN_HEIGHT, MOUTH_OPEN_SHORT_FRAMES, MOUTH_OPEN_LONG_FRAMES, MOUTH_CLOSED_FRAMES,
    MOUTH_FROWN, MOUTH_NOSE_SCRUNCH, MOUTH_SNARL, MOUTH_DUCKFACE,
    BROW_RAISE_LEFT, BROW_RAISE_RIGHT, BROWS_RAISE, WAIT_FRAMES
)
from command_mapper.gesture_actions import type_and_remember
from gestures.detectors.eye_detector import process_eyes
from gestures.detectors.eyebrow_detector import process_eyebrows
from gestures.detectors.mouth_detecor import process_mouth

class GestureEngine:
    def __init__(self):
        self.blinking = False
        self.blink_count = 0
        self.blinking_frames = 0
        
        self.squinting = False
        self.squinting_frames = 0
        
        self.bugeyed = False
        self.bugeyed_frames = 0
        
        self.winkedR = False
        self.winkedR_frames = 0
        
        self.winkedL = False
        self.winkedL_frames = 0
        
        self.mouth_open = False
        self.mouth_open_frames = 0
        self.mouth_closed_frames = 0
        
        self.mouth_scrunched = False
        self.mouth_scrunched_count = 0
        self.mouth_scrunched_frames = 0
        
        self.duckfacing = False
        
        self.brows_raised = False
        self.brows_raised_count = 0
        self.brows_raised_frames = 0
        
        self.command_on = False
        self.control_on = False
        self.shift_on = False
        
        self.current_keys = ''
        self.last_typed = ''

    def get_aspect_ratio(self, top, bottom, right, left):
        height = dist.euclidean([top.x, top.y], [bottom.x, bottom.y])
        width = dist.euclidean([right.x, right.y], [left.x, left.y])
        return height / width

    def timeout_double(self, state, frames):
        if state:
            frames += 1
        if frames > WAIT_FRAMES:
            frames = 0
            state = False
        return state, frames

    def process_gestures(self, face):
        # Face position processing
        face_mid_right = face[234]
        face_mid_left = face[454]
        face_mid_top = face[10]
        face_mid_bottom = face[152]
        cheek_mid_right = face[50]
        cheek_mid_left = face[280]

        if cheek_mid_right.x < face_mid_right.x:
            print("head turn R")
            return False
        elif cheek_mid_left.x > face_mid_left.x:
            print("head turn L")
            return False

        face_angle = (face_mid_top.x - face_mid_bottom.x) / (
            face_mid_right.x - face_mid_left.x)
        if face_angle > FACE_TILT:
            print("head tilt R", face_angle)
        elif face_angle < -FACE_TILT:
            print("head tilt L", face_angle)

        # Eye processing
        process_eyes(self, face)
        
        # Mouth processing (now modularized)
        process_mouth(self, face, face_mid_top, face_mid_bottom, face_mid_right, face_mid_left)
        
        # Eyebrow processing
        process_eyebrows(self, face)

        return True