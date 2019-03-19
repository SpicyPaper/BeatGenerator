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

    def random(self, tracks):
        start_time = time.clock()
        self.printTitle("Random Tracks Algorithm (%d tracks)" % tracks)
        for i in range(tracks):
            channel = i
            tempo = random.randint(30, 100)
            notes = []
            for j in range (getNumberNote(self.clip.duration, tempo)):
                notes.append(random.randint(30, 60))
            self.result.append((channel, tempo, notes))
            self.printProgress(i + 1, tracks)
        time.sleep(1)
        self.printResult(time.clock() - start_time)

    def printTitle(self, algoName):
        print("     ____             __     ______                           __            ")
        print("    / __ )___  ____ _/ /_   / ____/__  ____  ___  _________ _/ /_____  _____")
        print("   / __  / _ \/ __ `/ __/  / / __/ _ \/ __ \/ _ \/ ___/ __ `/ __/ __ \/ ___/")
        print("  / /_/ /  __/ /_/ / /_   / /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /    ")
        print(" /_____/\___/\__,_/\__/   \____/\___/_/ /_/\___/_/   \__,_/\__/\____/_/     ")
        print("\n                                                 Traitement d'image - 2019")
        print("\n  Using:", algoName);

    def printProgress(self, current, max):
        progress = int(100 * current / max)
        if (progress < 100):
            print("  Computation progress: %d" % progress, "%", end='\r')
        else:
            print("  Computation progress: %d" % progress, "%")

    def printResult(self, time):
        print("  Time taken: %d" % time, "second(s)")


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
    # TODO use that to get the first argument as the filename to use
    # # Set an argument parser
    # parser = argparse.ArgumentParser(description='Convert a video file (.avi) to a music.')
    # parser.add_argument('filename', metavar='filename',
    #                     help='a video file')

    # args = vars(parser.parse_args())

    cap = cv2.VideoCapture('Class_Room_Tour.avi')
    degrees = []  # MIDI note number
    counter = 0
    
    # Get the duration of the video
    clip = VideoFileClip("Class_Room_Tour.avi")

    gen = BeatGenerator(clip)
    gen.random(4)

    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 50   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    # Define the number of note the music must have according to the tempo
    numberOfNote = getNumberNote(clip.duration, tempo)

    # Generate the correct number of note to have a music of the desired length
    for i in range(numberOfNote):
        degrees.append(random.randint(10, 100))

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                        # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    with open("major-scale.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)