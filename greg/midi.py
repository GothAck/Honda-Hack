import sys
import os
import random

import pygame
import pygame.midi
from pygame.locals import *

from time import sleep

import copy

device_id = 2

try:
    device_id = int( sys.argv[-1] )
except:
    pass


instrument = 19
anchor_note = 60

BEATS_PER_BAR = 16

chords = {
  'major': (2,2,1,2,2,2,1),
}

major_scale = {
  0: 0,
  2: 1,
  4: 2,
  5: 3,
  7: 4,
  9: 5,
  11: 6,
}

chord_relativity = {
  'major': [ 2, 4],
  'power': [ 4, 7],
  'inv1' : [-3,-5],
  'inv2' : [-3, 2],
}

drum_modes = [
    [36, 40, 45, 50, 57]
]


chord_progressions = [
    [ 0,-3,-2,-5],
    [ 0, 1, 3, 4],
    [ 5, 2, 0, 1],
    [-2,-3,-4,-3],
]

drum_mode = 0


major_scale_reversed = dict((v,k) for k, v in major_scale.iteritems())

tick_time = 4

def to_relative(note_in):
    note_off = note_in - anchor_note
    note = note_off % 12
    offset = note_off / 12 * len(major_scale)
    major_note = major_scale.get(note)
    if major_note:
        return major_note + offset
    return None

def from_relative(note):
    n = major_scale_reversed.get(note % len(major_scale))
    if n:
      return (anchor_note + n) + (n/len(major_scale))*12
    return None # This should never happen

def random_fill():
    drums = drum_modes[drum_mode]
    fill = []
    for i in range(4):
        drum = random.choice(drums + [None])
        if drum:
            fill.append((True, drum))
        else:
            fill.append(None)
    return fill

def random_relative_from_chord_root(chord):
    """
    When we are playing a chord, only some notes fit in when being backing.
    Pick a random note in the chord set using chord_relativity
    """
    return random.choice(chord_relativity[random.choice(chord_relativity.keys())])
  

def generate_next_bar (bar_queue, bar_no):
    prev_bar = bar_queue[-1]
    next_bar = copy.deepcopy(prev_bar)

    if not bar_no % 4:
        print "RANDOM FILL TIME!"
        bar_queue.append( {9: random_fill(), 'length':4});

    print "--------------------------------------------------"
    
    # Increment the prgression
    chord_progression, chord_progression_index = next_bar['progression']
    relative_next_chord = chord_progressions[chord_progression][(chord_progression_index+1)%len(chord_progressions[0])]
    print "relative_next_chord: %s" % relative_next_chord
    next_bar['progression'] = (chord_progression, relative_next_chord)
    
    #Populate Next bar with note
    #next_bar[2] = [(True,relative_next_chord) for i in range(BEATS_PER_BAR)]
    next_bar[2] = [(True,relative_next_chord)] + [None]*(BEATS_PER_BAR-2) + [(False,relative_next_chord)]
    
    next_bar[3] = [(True,relative_next_chord)]*BEATS_PER_BAR
    
    # Mutate line
    for i in range(len(next_bar[3])):
        if random.randint(0,4)==0:
          next_bar[3][i] = (True, random_relative_from_chord_root(next_bar[3][i][1]))
    
    print next_bar
    
    
    print "--------------------------------------------------"
    
    if not bar_no % 8:
      global anchor_note
      anchor_note += random.randint(-4,4)
      #global tick_time
      #tick_time   += 1
    
    bar_queue.append(next_bar)


def main(argv):
    pygame.init()

    running = True
    notes_on = {}
    clock = pygame.time.Clock()

    pygame.midi.init()
    midi_out = pygame.midi.Output(device_id, 0)
    midi_out.set_instrument(50,2)
    midi_out.set_instrument(36,3)
    bar_queue = [
        {
            #1:  [(True, 2, 'major'), (True, 0), (True, 4), None, (False, 2), (False, 0), (False, 4), None],
            9:  [(True, 36), (False, 36)] * 8,
            'progression': (0,0),
        }
    ]
    bar = 0
    beat = 0
    current_bar = bar_queue[0]
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        break
            print 'iteration', bar, beat, anchor_note
            for channel in current_bar:
                if not isinstance(channel, (int, long)): continue
                current_channel = current_bar[channel]
                if beat < len(current_channel):
                    current_beat = current_channel[beat]
                    if current_beat:
                        on_off = current_beat[0]
                        our_notes = [(0 if channel == 9 else anchor_note) + current_beat[1]]
                        if len(current_beat) == 3:
                            print 'pppppppppppppppppppppppppppppppppppppppppppppppppppp', to_relative(our_notes[0])
                            print 'chord!!!'
                            pass
                        for our_note in our_notes:
                            if current_beat[0]:
                                midi_out.note_on(our_note, 127, channel)
                                if channel not in notes_on:
                                    notes_on[channel] = set()
                                notes_on[channel].add(our_note)
                            else:
                                midi_out.note_off(our_note, None, channel)
                                notes_on[channel].remove(our_note)
            beat += 1
            if beat >= current_bar.get('length', BEATS_PER_BAR):
                bar += 1
                if bar >= len(bar_queue):
                    print 'Run out of bars!'
                    # Right, percussion instuments rarely get note_off called on them, clean up here
                    for note in notes_on[9]:
                        midi_out.note_off(note, None, 9)
                    notes_on[9] = set()
                    generate_next_bar(bar_queue, bar)
                    #bar_queue.append(generate_next_bar())
                    #running = False
                    #continue
                beat = 0
                current_bar = bar_queue.pop(0)
            clock.tick(tick_time)
    except KeyboardInterrupt:
        pass
    for channel in notes_on:
        for note in notes_on[channel]:
            midi_out.note_off(note, channel)
    midi_out.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
