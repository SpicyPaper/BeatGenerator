from midiutil import MIDIFile
import numpy as np
import cv2
import sys
import argparse
import random
import time
from moviepy.video.io.VideoFileClip import VideoFileClip

class BeatGenerator:

    def __init__(self, clip):
        self.result = []
        self.clip = clip;

    def __printTitle(self, algoName):
        print("     ____             __     ______                           __            ")
        print("    / __ )___  ____ _/ /_   / ____/__  ____  ___  _________ _/ /_____  _____")
        print("   / __  / _ \/ __ `/ __/  / / __/ _ \/ __ \/ _ \/ ___/ __ `/ __/ __ \/ ___/")
        print("  / /_/ /  __/ /_/ / /_   / /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /    ")
        print(" /_____/\___/\__,_/\__/   \____/\___/_/ /_/\___/_/   \__,_/\__/\____/_/     ")
        print("\n                                                 Traitement d'image - 2019")
        print("\n  Using:", algoName);

    def __printProgress(self, current, max):
        progress = int(100 * current / max)
        current = int(progress / 2)
        print(" [", end='')
        for i in range (current):
            print("=", end='')
        for i in range (50 - current):
            print(" ", end='')
        print("]", end='')

        if (progress < 100):
            print(" %d" % progress, "%", end='\r')
        else:
            print(" %d" % progress, "%")

    def __printResult(self, time):
        print("  Time taken: %d" % time, "second(s)")

    def random(self, tracks):
        start_time = time.clock()
        self.__printTitle("Random Tracks Algorithm (%d tracks)" % tracks)
        for i in range(tracks):
            track = i
            tempo = random.randint(30, 100)
            notes = []
            for j in range (getNumberNote(self.clip.duration, tempo)):
                notes.append(random.randint(30, 60))
            self.result.append((track, tempo, notes))
            self.__printProgress(i + 1, tracks)
        self.__printResult(time.clock() - start_time)

    def getMIDI(self):
        nb_tracks = len(self.result)
        MIDI = MIDIFile(nb_tracks)

        j = 0
        for track, tempo, notes in self.result:
            MIDI.addTempo(track, 0, tempo)
            for i, note in enumerate(notes):
                MIDI.addProgramChange(track, i, i, 109 + j)
                MIDI.addNote(track, i, note, i, 1, 100)
            j += 1
        
        return MIDI



def averageRGB(frame, everyNPixels):
    """
    Compute the average color of a given video
    """
    averageR = averageRGBChoice(frame, 0, everyNPixels)
    averageG = averageRGBChoice(frame, 1, everyNPixels)
    averageB = averageRGBChoice(frame, 2, everyNPixels)

    averageColor = int((averageR + averageG + averageB) / 3)

    print(averageColor)

    return averageColor

def averageRGBChoice(frame, colorStage, everyNPixels):
    """
    Compute the average of red, green or blue.
    frame : the images
    colorStage : 0 = red, 1 = green, 2 = blue
    everyNPixels : take one pixel every n pixels
    """
    vect = frame.shape
    dimX = vect[0]
    dimY = vect[1]
    dimZ = vect[2]

    nbPixels = 0
    averageColor = 0

    for x in range(0, dimX):
        for y in range(0, dimY):
            if (x * y) % everyNPixels == 0:
                nbPixels += 1
                averageColor += frame[x][y][colorStage]
    
    # [0 ; 255 / 4]
    averageColor = int(averageColor / nbPixels / 4)

    return averageColor

def getNumberNote(musicDuration, tempo):
    """
    Return the number of notes that the music must have to be of the specified duration
    musicDuration : the duration of the music (in seconds)
    tempo : the number of BMP of the music
    """
    durationInMinute = musicDuration / 60
    return int(tempo * durationInMinute)



if __name__ == "__main__":

    clip = VideoFileClip("Class_Room_Tour.avi")
    gen = BeatGenerator(clip)
    gen.random(4)
    MIDI = gen.getMIDI()

    with open("major-scale.mid", "wb") as output_file:
        MIDI.writeFile(output_file)