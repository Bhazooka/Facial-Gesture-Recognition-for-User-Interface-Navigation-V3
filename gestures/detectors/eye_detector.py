import keyboard
import pyautogui
from config.settings import (
    EYE_BLINK_HEIGHT, EYE_SQUINT_HEIGHT, EYE_OPEN_HEIGHT, EYE_BUGGED_HEIGHT, WAIT_FRAMES
)
import screeninfo

def get_screen_size():
    # Get the primary monitor's size
    screen = screeninfo.get_monitors()[0]
    return screen.width, screen.height

def estimate_gaze(face):
    # Example: Use the right eye for gaze estimation
    # You may need to adjust indices for your model
    eye_center = face[468]  # Example: iris center
    eye_left = face[133]
    eye_right = face[33]
    eye_top = face[159]
    eye_bottom = face[145]

    # Normalize iris position within the eye rectangle
    x_ratio = (eye_center.x - eye_left.x) / (eye_right.x - eye_left.x)
    y_ratio = (eye_center.y - eye_top.y) / (eye_bottom.y - eye_top.y)
    return x_ratio, y_ratio

def process_eyes(engine, face):
    # Eye measurements
    from scipy.spatial import distance as dist

    def get_aspect_ratio(top, bottom, right, left):
        height = dist.euclidean([top.x, top.y], [bottom.x, bottom.y])
        width = dist.euclidean([right.x, right.y], [left.x, left.y])
        return height / width

    eyeR_top = face[159]
    eyeR_bottom = face[145]
    eyeR_inner = face[133]
    eyeR_outer = face[33]
    eyeR_ar = get_aspect_ratio(eyeR_top, eyeR_bottom, eyeR_outer, eyeR_inner)

    eyeL_top = face[386]
    eyeL_bottom = face[374]
    eyeL_inner = face[362]
    eyeL_outer = face[263]
    eyeL_ar = get_aspect_ratio(eyeL_top, eyeL_bottom, eyeL_outer, eyeL_inner)
    eyeA_ar = (eyeR_ar + eyeL_ar) / 2

    # Eye gesture detection
    engine.command_on = False
    engine.shift_on = False
    engine.squinting = False
    engine.bugeyed = False

    if eyeR_ar < EYE_BLINK_HEIGHT:
        if eyeL_ar > EYE_OPEN_HEIGHT:
            print("R wink", eyeR_ar)
            engine.shift_on = True
            engine.winkedR = True
            if engine.winkedL and (engine.winkedL_frames < WAIT_FRAMES):
                print("ESCAPE")
                keyboard.press_and_release('escape')
                engine.winkedL_frames = 0
                engine.winkedL = False
        elif eyeR_ar < EYE_BLINK_HEIGHT:
            if not engine.blinking:
                engine.blink_count += 1
                print("blink", engine.blink_count)
                if engine.duckfacing and engine.blink_count == 2:
                    print("BACKSPACE")
                    keyboard.press_and_release("backspace")
            engine.blinking = True
    elif eyeL_ar < EYE_BLINK_HEIGHT and eyeR_ar > EYE_OPEN_HEIGHT:
        print("L wink", eyeL_ar)
        engine.command_on = True
        engine.winkedL = True
        if engine.winkedR and (engine.winkedR_frames < WAIT_FRAMES):
            print("clear Morse queue")
            engine.current_morse = ''
            engine.winkedR_frames = 0
            engine.winkedR = False
    elif eyeA_ar < EYE_SQUINT_HEIGHT:
        engine.squinting = True
        engine.squinting_frames += 1
        if engine.squinting_frames > WAIT_FRAMES:
            print("squint", eyeA_ar)
            keyboard.press_and_release("command+-")
            engine.squinting_frames = 0
    elif eyeA_ar > EYE_BUGGED_HEIGHT:
        engine.bugeyed = True
        engine.bugeyed_frames += 1
        if engine.bugeyed_frames > WAIT_FRAMES:
            engine.bugeyed_frames = 0
            print("big eyes", eyeA_ar)
            keyboard.press_and_release("command+shift+=")
    else:
        engine.blinking = False

    engine.winkedL, engine.winkedL_frames = engine.timeout_double(engine.winkedL, engine.winkedL_frames)
    engine.winkedR, engine.winkedR_frames = engine.timeout_double(engine.winkedR, engine.winkedR_frames)
    engine.blink_count, engine.blinking_frames = engine.timeout_double(engine.blink_count, engine.blinking_frames)

    # --- Gaze tracking and mouse control ---
    try:
        x_ratio, y_ratio = estimate_gaze(face)
        screen_w, screen_h = get_screen_size()
        # Clamp ratios between 0 and 1
        x_ratio = min(max(x_ratio, 0), 1)
        y_ratio = min(max(y_ratio, 0), 1)
        # Map to screen coordinates
        mouse_x = int(x_ratio * screen_w)
        mouse_y = int(y_ratio * screen_h)
        pyautogui.moveTo(mouse_x, mouse_y, duration=0.1)
    except Exception as e:
        print("Gaze estimation failed:", e)