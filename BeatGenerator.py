from midiutil import MIDIFile
import numpy as np
import cv2

cap = cv2.VideoCapture('Farid_Hello.avi')
degrees = []  # MIDI note number
counter = 0

while(cap.isOpened()):
    ret, frame = cap.read()

    if frame is None:
        break
    else:
        if counter % 10 == 0:
            degrees.append(int(frame[10][25][0] / 4))
        counter += 1

cap.release()
cv2.destroyAllWindows()

track    = 0
channel  = 0
time     = 0    # In beats
duration = 1    # In beats
tempo    = 200   # In BPM
volume   = 100  # 0-127, as per the MIDI standard

MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
MyMIDI.addTempo(track, time, tempo)

for i, pitch in enumerate(degrees):
    MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

with open("major-scale.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)