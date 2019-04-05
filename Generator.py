import argparse
import random
import sys
import time

import cv2
import numpy as np
from midiutil import MIDIFile
from moviepy.video.io.VideoFileClip import VideoFileClip

from Track import Track


class Generator:
    
    def __init__(self, videoName):
        self.result = []
        self.tracks = []
        self.videoName = videoName
        self.clip = VideoFileClip('Videos/' + videoName + '.avi')

    def __printTitle(self, algoName):
        print("     ____             __     ______                           __            ")
        print("    / __ )___  ____ _/ /_   / ____/__  ____  ___  _________ _/ /_____  _____")
        print("   / __  / _ \/ __ `/ __/  / / __/ _ \/ __ \/ _ \/ ___/ __ `/ __/ __ \/ ___/")
        print("  / /_/ /  __/ /_/ / /_   / /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /    ")
        print(" /_____/\___/\__,_/\__/   \____/\___/_/ /_/\___/_/   \__,_/\__/\____/_/     ")
        print("\n                                                 Traitement d'image - 2019")
        print("\n  Using:", algoName)

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

    def __getNumberNotes(self, musicDuration, tempo):
        """
        Return the number of notes that the music must
        have to be of the specified duration

        musicDuration :     the duration of the music (in seconds)
        tempo :             the number of BMP of the music
        """
        durationInMinute = musicDuration / 60
        return int(tempo * durationInMinute)

    def getMIDI(self):
        return MIDIFile(1)

    """
    TODO see what to do with that
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
        
        return MIDI"""

    def random(self, tracks):
        start_time = time.clock()
        self.__printTitle("Random Tracks Algorithm (%d tracks)" % tracks)
        for i in range(tracks):
            track = i
            tempo = random.randint(30, 100)
            notes = []
            for j in range (self.__getNumberNotes(self.clip.duration, tempo)):
                notes.append(random.randint(30, 60))
            self.result.append((track, tempo, notes))
            self.__printProgress(i + 1, tracks)
        self.__printResult(time.clock() - start_time)

    def diffBetween2Images(self, videoName, maxSound, factor, everyNImages, th):
        """
        Return all notes compute based on the diff between
        2 consecutives frame of the video

        videoName :     the video file name without extension
        maxSound :      max value that can be returned for a sound
        factor :        applied on the note, should be big if the video
                            is quiet, should be low if the video is agitated
        everyNImages :  take only n images of the video
        th :            the threshold [0 ; 255]
        """
        cap = self.videoCap(videoName)
        degrees = []  # MIDI note number
        counter = 0
        previousNbOfDiff = -1

        if(cap.isOpened()):
            ret, frame = cap.read()
        
        while(cap.isOpened()):
            previousFrame = frame
            ret, frame = cap.read()

            if frame is None:
                break
            else:
                if counter % everyNImages == 0:
                    previousNbOfDiff, sound = self.__diffBetween2Images(maxSound, factor, previousNbOfDiff, previousFrame, frame, th)
                    if sound != -1:
                        degrees.append(sound)
                counter += 1

        return degrees

    def __diffBetween2Images(self, maxSound, factor, previousNbOfDiff, previousFrame, frame, th):
        
        diff = cv2.absdiff(previousFrame, frame)
        mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        imask = mask > th
        nbOfDiff = np.sum(imask)

        if previousNbOfDiff == -1:
            return nbOfDiff, -1
        else:
            frameSize = np.sum(np.ones_like(frame, np.uint8))
            diffBetweenDiff = np.absolute(nbOfDiff - previousNbOfDiff)
            
            sound = int(diffBetweenDiff / frameSize * maxSound * factor)

            if sound > maxSound:
                sound = maxSound

            return np.sum(imask), sound

    def __diffBetween2Images_display(self, previousFrame, frame, th, imgCounter):
        
        diff = cv2.absdiff(previousFrame, frame)
        mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        imask = mask > th

        canvas = np.zeros_like(frame, np.uint8)
        canvas[imask] = frame[imask]

        cv2.imwrite("DiffImages/result" + str(imgCounter) + ".png", canvas)

    def averageRGB(self, everyNPixels, everyNImages):
        """
        Return all notes compute based on average color of
        a given video

        everyNPixels :      take only n pixels of the image
        everyNImages :      take only n images of the video
        """

        track = Track(0, 1, 2)
        # TODO The tempo, volume and the duration could change depending on the algo
        tempo = 200
        # TODO The method __getNumberNotes has to accept the duration in order to compute the correct number of notes per bloc
        duration = 1
        volume = 100

        cap = self.videoCap(self.videoName)
        notes = []
        notesNumberPerBloc = self.__getNumberNotes(track.blocDuration, tempo)
        print(notesNumberPerBloc)
        imagesCounter = 0
        notesCounter = 0

        if(cap.isOpened()):
            ret, frame = cap.read()
        
        while(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounter += 1

            if frame is None:
                break
            else:
                if imagesCounter % everyNImages == 0:
                    averageR = self.__averageRGBChoiceOneFrame(frame, 0, everyNPixels)
                    averageG = self.__averageRGBChoiceOneFrame(frame, 1, everyNPixels)
                    averageB = self.__averageRGBChoiceOneFrame(frame, 2, everyNPixels)

                    note = int((averageR + averageG + averageB) / 3 / 4)
                    print(note)

                    notesCounter += 1
                    notes.append(track.createNoteVolTuple(note, volume))
                
                    # Test if one bloc can be done
                    if notesCounter % notesNumberPerBloc == 0:
                        track.addBlocInfo(duration, tempo)
                        track.addNotes(notes)
                        notes = []

        if len(notes) > 0:
            track.addBlocInfo(duration, tempo)
            track.addNotes(notes)

        self.tracks.append(track)

    def averageRGBChannel(self, videoName, everyNPixels, everyNImages, colorChannel):
        """
        Return all notes compute based on average red, green
        or blue channel of a given video

        videoName :         the video file name without extension
        everyNPixels :      take only n pixels of the image
        everyNImages :      take only n images of the video
        colorChannel :      0 = red, 1 = green, 2 = blue
        """

        cap = self.videoCap(videoName)
        degrees = []  # MIDI note number
        imagesCounter = 0

        if(cap.isOpened()):
            ret, frame = cap.read()
        
        while(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounter += 1

            if frame is None:
                break
            else:
                if imagesCounter % everyNImages == 0:
                    averageColorChannel = self.__averageRGBChoiceOneFrame(frame, colorChannel, everyNPixels) / 4
                    degrees.append(averageColorChannel)

        return degrees

    def __averageRGBChoiceOneFrame(self, frame, colorChannel, everyNPixels):
        """
        Compute a sound between [0 ; 255 / 4] based on the average of
        red, green or blue in a given frame.

        frame :             the images
        colorChannel :      0 = red, 1 = green, 2 = blue
        everyNPixels :      take one pixel every n pixels on the image
        """

        vect = frame.shape
        dimX = vect[0]
        dimY = vect[1]

        nbPixels = 0
        averageColor = 0

        for x in range(0, dimX):
            for y in range(0, dimY):
                if (x * y) % everyNPixels == 0:
                    nbPixels += 1
                    averageColor += frame[x][y][colorChannel]

        # [0 ; 255]
        averageColor = int(averageColor / nbPixels)

        return averageColor

    def videoCap(self, videoName):
        """
        
        """
        cap = cv2.VideoCapture('Videos/' + videoName + '.avi')
        return cap
