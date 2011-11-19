import sys
import os

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

drum_modes = [
    [36, 40, 45, 50, 57]
]

chord_progressions = [
    [ 0,-3,-2,-4],
    [ 0, 1, 3, 4],
    [ 5, 2, 0, 1],
    [-2,-3,-4,-3],
]

major_scale_reversed = dict((v,k) for k, v in major_scale.iteritems())

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

def random_fill(stuff):
    
    pass    

def generate_next_bar (bar_queue):
    prev_bar = bar_queue[-1]
    next_bar = copy.deepcopy(prev_bar)
    
    print "--------------------------------------------------"
    
    # Increment the prgression
    chord_progression, chord_progression_index = next_bar['progression']
    relative_next_chord = chord_progressions[chord_progression][(chord_progression_index+1)%len(chord_progressions[0])]
    print "relative_next_chord: %s" % relative_next_chord
    next_bar['progression'] = (chord_progression, relative_next_chord)
    
    #Populate Next bar with note
    next_bar[2] = [(True,from_relative(relative_next_chord)) for i in range(BEATS_PER_BAR)]
    
    print next_bar[2]
    
    
    print "--------------------------------------------------"
    
    bar_queue.append(next_bar)

if __name__ == '__main__':
    pygame.init()

    running = True
    notes_on = {}
    clock = pygame.time.Clock()

    pygame.midi.init()
    port = device_id
    midi_out = pygame.midi.Output(port, 0)
#    midi_out.set_instrument(10,0)
#    midi_out.set_instrument(20,1)
    bar_queue = [
        {
            1:  [(True, 0, ), (True, 2), (True, 4), None, (False, 0), (False, 2), (False, 4), None],
            10: [(True, 36), (False, 36), (True, 36), (False, 36), (True, 36), (False, 36), (True, 36), (False, 36)],
            'progression': (0,0),
        }
    ]
    bar = 0
    beat = 0
    current_bar = bar_queue[0]
    print 'beginning loop', current_bar
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        break
            print 'iteration', bar, beat
            for channel in current_bar:
                if not isinstance(channel, (int, long)): continue
                print 'channel', channel
                current_channel = current_bar[channel]
                if beat < len(current_channel):
                    current_beat = current_channel[beat]
                    print 'has beat', current_beat
                    if current_beat:
                        print type(current_beat)
                        print current_beat[0]
                        on_off = current_beat[0]
                        our_note = (0 if channel == 10 else anchor_note) + current_beat[1]
                        if current_beat[0]:
                            midi_out.note_on(our_note, 127, channel)
                            if channel not in notes_on:
                                notes_on[channel] = set()
                            notes_on[channel].add(our_note)
                        else:
                            midi_out.note_off(our_note, None, channel)
                            notes_on[channel].remove(our_note)
            beat += 1
            if beat >= BEATS_PER_BAR:
                bar += 1
                if bar >= len(bar_queue):
                    print 'Run out of bars!'
                    generate_next_bar(bar_queue)
                    #bar_queue.append(generate_next_bar())
                    #running = False
                    #continue
                beat = 0
                current_bar = bar_queue.pop(0)
            clock.tick(4)
    except KeyboardInterrupt:
        pass
    for channel in notes_on:
        for note in notes_on[channel]:
            midi_out.note_off(note, channel)
    print "RAJLRJSHHSJHADHKJASRA"
