from config.settings import (
    MOUTH_OPEN_HEIGHT, MOUTH_OPEN_SHORT_FRAMES, MOUTH_OPEN_LONG_FRAMES, MOUTH_CLOSED_FRAMES,
    MOUTH_FROWN, MOUTH_NOSE_SCRUNCH, MOUTH_SNARL, MOUTH_DUCKFACE, WAIT_FRAMES
)
from command_mapper.gesture_actions import type_and_remember

def process_mouth(engine, face, face_mid_top, face_mid_bottom, face_mid_right, face_mid_left):
    mouth_outer_top = face[0]
    mouth_outer_bottom = face[17]
    mouth_outer_right = face[61]
    mouth_outer_left = face[291]

    mouth_inner_top = face[13]
    mouth_inner_bottom = face[14]
    mouth_inner_right = face[78]
    mouth_inner_left = face[308]
    mouth_inner_ar = engine.get_aspect_ratio(
        mouth_inner_top, mouth_inner_bottom, mouth_inner_right, mouth_inner_left)

    nose_bottom = face[2]

    engine.mouth_open = mouth_inner_ar > MOUTH_OPEN_HEIGHT
    if engine.mouth_open:
        print("mouth open", mouth_inner_ar)
        engine.mouth_open_frames += 1

    if (not engine.mouth_open) and (engine.mouth_open_frames >= MOUTH_OPEN_SHORT_FRAMES):
        if engine.mouth_closed_frames >= MOUTH_CLOSED_FRAMES:
            if engine.mouth_open_frames >= MOUTH_OPEN_LONG_FRAMES:
                engine.current_morse += '-'
            elif engine.mouth_closed_frames >= MOUTH_CLOSED_FRAMES:
                engine.current_morse += '.'
            engine.mouth_open_frames = 0
            engine.mouth_closed_frames = 0
        else:
            engine.mouth_closed_frames += 1

    mouth_frowny_right = (mouth_inner_right.y - mouth_inner_bottom.y) > MOUTH_FROWN
    mouth_frowny_left = (mouth_inner_left.y - mouth_inner_bottom.y) > MOUTH_FROWN
    mouth_frowny = mouth_frowny_right and mouth_frowny_left

    nose_to_mouth = (mouth_outer_top.y - nose_bottom.y) / (
        face_mid_bottom.y - face_mid_top.y)

    if (engine.mouth_scrunched_count > 0) and (not engine.mouth_scrunched):
        engine.mouth_scrunched_frames += 1

    if (nose_to_mouth < MOUTH_NOSE_SCRUNCH) and mouth_frowny:
        engine.current_morse, engine.last_typed = type_and_remember(
            engine.current_morse, engine.last_typed, engine.command_on, engine.control_on, engine.shift_on)
        engine.current_morse = ''
        if not engine.mouth_scrunched:
            engine.mouth_scrunched_count += 1
            print("mouth scrunch", nose_to_mouth)
        engine.mouth_scrunched = True
    else:
        engine.mouth_scrunched = False

    if engine.mouth_scrunched_count >= 3:
        print("triple scrunch: ENTER")
        engine.current_morse = 'enter'
        engine.current_morse, engine.last_typed = type_and_remember(
            engine.current_morse, engine.last_typed, engine.command_on, engine.control_on, engine.shift_on)
        engine.mouth_scrunched_frames = 0
        engine.mouth_scrunched_count = 0
    elif engine.mouth_scrunched_count == 2:
        if engine.mouth_scrunched_frames > WAIT_FRAMES:
            print("double scrunch: SPACE")
            engine.current_morse = 'space'
            engine.current_morse, engine.last_typed = type_and_remember(
                engine.current_morse, engine.last_typed, engine.command_on, engine.control_on, engine.shift_on)
            engine.mouth_scrunched_frames = 0
            engine.mouth_scrunched_count = 0
    elif (engine.mouth_scrunched_count == 1) and (engine.mouth_scrunched_frames > WAIT_FRAMES):
        engine.mouth_scrunched_frames = 0
        engine.mouth_scrunched_count = 0

    # Check for duckface
    mouth_outer_right_mid_top = face[39]
    mouth_outer_right_mid_bottom = face[181]
    mouth_outer_left_mid_top = face[269]
    mouth_outer_left_mid_bottom = face[405]

    # Check for snarl (unused)
    mouth_snarl_right = (mouth_outer_left_mid_top.y - mouth_outer_right_mid_top.y) / (
        face_mid_right.y - face_mid_left.y)
    if mouth_snarl_right > MOUTH_SNARL:
        print("snarl R", mouth_snarl_right)

    engine.duckfacing = False
    if not engine.mouth_open:
        mouth_width = (mouth_outer_right.x - mouth_outer_left.x) / (
            face_mid_right.x - face_mid_left.x)
        mouth_height_right = mouth_outer_right_mid_top.y - mouth_outer_right_mid_bottom.y
        mouth_height_left = mouth_outer_left_mid_top.y - mouth_outer_left_mid_bottom.y
        mouth_height = (mouth_height_right + mouth_height_left) / (
            face_mid_top.y - face_mid_bottom.y)
        mouth_outer_ar = mouth_width / mouth_height
        if mouth_outer_ar < MOUTH_DUCKFACE:
            print("duckface", mouth_outer_ar)
            engine.duckfacing = True