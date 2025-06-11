import cv2
import keyboard
from config.settings import (
    BROW_RAISE_LEFT, BROW_RAISE_RIGHT, BROWS_RAISE, WAIT_FRAMES
)

def process_eyebrows(engine, face):
    import mediapipe as mp
    eyeR_top = face[159]
    browR_top = face[52]
    browR_bottom = face[223]
    
    browR_eyeR_lower_dist = mp.solutions.drawing_utils._normalized_to_pixel_coordinates(
        browR_bottom.x, browR_bottom.y, 640, 480)
    browR_eyeR_upper_dist = mp.solutions.drawing_utils._normalized_to_pixel_coordinates(
        browR_top.x, browR_top.y, 640, 480)
    eyeR_top_px = mp.solutions.drawing_utils._normalized_to_pixel_coordinates(
        eyeR_top.x, eyeR_top.y, 640, 480)
    
    browR_eyeR_dist = 0
    if browR_eyeR_lower_dist and browR_eyeR_upper_dist and eyeR_top_px:
        browR_eyeR_lower_dist = cv2.norm(
            (browR_eyeR_lower_dist[0] - eyeR_top_px[0], browR_eyeR_lower_dist[1] - eyeR_top_px[1]))
        browR_eyeR_upper_dist = cv2.norm(
            (browR_eyeR_upper_dist[0] - eyeR_top_px[0], browR_eyeR_upper_dist[1] - eyeR_top_px[1]))
        browR_eyeR_dist = (browR_eyeR_lower_dist + browR_eyeR_upper_dist) / 2

    browL_top = face[443]
    browL_bottom = face[257]
    eyeL_top = face[386]
    browL_eyeL_lower_dist = mp.solutions.drawing_utils._normalized_to_pixel_coordinates(
        browL_bottom.x, browL_bottom.y, 640, 480)
    browL_eyeL_upper_dist = mp.solutions.drawing_utils._normalized_to_pixel_coordinates(
        browL_top.x, browL_top.y, 640, 480)
    eyeL_top_px = mp.solutions.drawing_utils._normalized_to_pixel_coordinates(
        eyeL_top.x, eyeL_top.y, 640, 480)
    
    browL_eyeL_dist = 0
    if browL_eyeL_lower_dist and browL_eyeL_upper_dist and eyeL_top_px:
        browL_eyeL_lower_dist = cv2.norm(
            (browL_eyeL_lower_dist[0] - eyeL_top_px[0], browL_eyeL_lower_dist[1] - eyeL_top_px[1]))
        browL_eyeL_upper_dist = cv2.norm(
            (browL_eyeL_upper_dist[0] - eyeL_top_px[0], browL_eyeL_upper_dist[1] - eyeL_top_px[1]))
        browL_eyeL_dist = (browL_eyeL_lower_dist + browL_eyeL_upper_dist) / 2

    if (face[152].y - face[10].y) != 0:
        brows_avg_raise = (browR_eyeR_dist + browL_eyeL_dist) / (
            face[152].y - face[10].y)
    else:
        brows_avg_raise = 0
    brows_relative_raise = browR_eyeR_dist - browL_eyeL_dist

    if brows_relative_raise < BROW_RAISE_LEFT:
        engine.brows_raised = False
        if engine.duckfacing:
            print("L brow duckfacing: ARROW LEFT", brows_relative_raise)
            keyboard.press_and_release("left arrow")
        else:
            print("L brow raise: SCROLL UP", brows_relative_raise)
            keyboard.press_and_release("up arrow")
    elif brows_relative_raise > BROW_RAISE_RIGHT:
        engine.brows_raised = False
        if engine.duckfacing:
            print("R brow duckfacing: ARROW RIGHT", brows_relative_raise)
            keyboard.press_and_release("right arrow")
        else:
            print("R brow raise: SCROLL DOWN", brows_relative_raise)
            keyboard.press_and_release("down arrow")
    elif brows_avg_raise > BROWS_RAISE:
        if not engine.brows_raised:
            engine.brows_raised_count += 1
        engine.brows_raised = True
        print("brows raised", brows_avg_raise)
    else:
        engine.brows_raised = False

    engine.control_on = engine.brows_raised

    if engine.brows_raised_count >= 2:
        print("double brow raise - repeat:", engine.last_typed)
        if len(engine.last_typed):
            keyboard.press_and_release(engine.last_typed)
        engine.brows_raised_frames = 0
        engine.brows_raised_count = 0
    elif engine.brows_raised_count == 1:
        engine.brows_raised_frames += 1
    if engine.brows_raised_frames > WAIT_FRAMES:
        engine.brows_raised_frames = 0
        engine.brows_raised_count = 0