import keyboard
from utils.morse import morse

def type_and_remember(current_morse, last_typed, command_on, control_on, shift_on):
    keys = []
    if command_on:
        keys.append('command')
    if control_on:
        keys.append('control')
    if shift_on:
        keys.append('shift')
    letter = morse.get(current_morse, '')
    if len(letter):
        keys.append(letter)
    keystring = '+'.join(keys)
    if len(keystring):
        print("keys:", keystring)
        keyboard.press_and_release(keystring)
        last_typed = keystring
    return '', last_typed