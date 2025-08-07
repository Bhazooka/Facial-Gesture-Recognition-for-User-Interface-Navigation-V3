import keyboard
from utils.keystrokes import KEY_STROKES

def type_and_remember(current_keys, last_typed, command_on, control_on, shift_on):
    keys = []
    if command_on:
        keys.append('command')
    if control_on:
        keys.append('control')
    if shift_on:
        keys.append('shift')
    letter = KEY_STROKES.get(current_keys, '')
    if len(letter):
        keys.append(letter)
    keystring = '+'.join(keys)
    if len(keystring):
        print("keys:", keystring)
        keyboard.press_and_release(keystring)
        last_typed = keystring
    return '', last_typed