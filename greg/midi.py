import sys
import os

import pygame
import pygame.midi
from pygame.locals import *

from time import sleep

device_id = 4
instrument = 19
start_note = 53


if __name__ == '__main__':
    pygame.init()
    pygame.midi.init()
    port = device_id
    midi_out = pygame.midi.Output(port, 0)
    midi_out.set_instrument(instrument)
    
    midi_out.note_on(start_note, 127)

    print midi_out

    sleep(1)

    midi_out.note_off(start_note)

    del midi_out
    pygame.midi.quit()
