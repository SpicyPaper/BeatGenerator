import argparse
import os
import random
import shutil
import sys
import time
from collections import OrderedDict
import math
from tqdm import tqdm

import cv2
import numpy as np
from ffmpy import FFmpeg
from midiutil import MIDIFile
from moviepy.video.io.VideoFileClip import VideoFileClip
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from Track import Track


class Generator:
    
    def __init__(self, videoName):
        self.rootPath = os.getcwd()
        self.result = []
        self.tracks = []
        self.lastTrackNum = 0
        self.trackNb = 5
        self.videoName = videoName
        self.videoPath = os.path.join(self.rootPath, 'Videos', self.videoName + '.avi')
        self.clip = VideoFileClip(self.videoPath)
        self.num = None
        self.instru = None
        self.blocDuration = None
        self.tempo = None
        self.volume = None
        self.midi = None
        self.midiPath = None
        self.mp3Path = None

    def printTitle(self):
        print("     ____             __     ______                           __            ")
        print("    / __ )___  ____ _/ /_   / ____/__  ____  ___  _________ _/ /_____  _____")
        print("   / __  / _ \/ __ `/ __/  / / __/ _ \/ __ \/ _ \/ ___/ __ `/ __/ __ \/ ___/")
        print("  / /_/ /  __/ /_/ / /_   / /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /    ")
        print(" /_____/\___/\__,_/\__/   \____/\___/_/ /_/\___/_/   \__,_/\__/\____/_/     ")
        print("\n                                                 Traitement d'image - 2019")
        print("\n  Progress:")

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
        return tempo / 60 * musicDuration

    def __computeTrackInfo(self, currentTrack):
        """
        Returns track information, like : 
        - number of notes per bloc
        - duration of a note
        - total number of image in the clip
        - take only one image every n images

        currentTrack : the current track
        """

        notesNbPerBloc = int(self.__getNumberNotes(currentTrack.blocDuration, self.tempo))
        if notesNbPerBloc == 0:
            notesNbPerBloc = 1
        noteDuration = currentTrack.blocDuration / notesNbPerBloc

        nbBlocInClip = self.clip.duration / currentTrack.blocDuration
        nbNeededNotes = notesNbPerBloc * nbBlocInClip
        totNbImgInClip = self.clip.fps * self.clip.duration

        everyNImages = int(totNbImgInClip / nbNeededNotes)

        return notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages

    def __computeTrackParams(self, usedNormedValue, blocDuration = 5, volume = 100):
        """
        Give a value to the track parameters if they are equal to None.
        All value are compute based on the used normed value.

        usedNormedValue : value to compute the parameters, should be [0 ; 1]
        blocDuration : the duration of a bloc of notes in secondes
        value : the volume of the notes [0 ; 100]
        """

        if self.num == None:
            if self.lastTrackNum >= self.trackNb:
                print("Their is no more available tracks, increase the number of track!")
            else:
                self.num = self.lastTrackNum
                self.lastTrackNum += 1

        if self.instru == None:
            self.instru = int(usedNormedValue * 126) + 1

        if self.blocDuration == None:
            self.blocDuration = blocDuration

        if self.tempo == None:
            self.tempo = int(usedNormedValue * 180) + 1

        if self.volume == None:
            self.volume = volume

    def __computeTrack(self, currentTrack, normedValue):
        """
        Update track parameters based on a frame of the video.

        currentTrack : the track that should be update
        normedValue : a normed value used to compute parameters [0 ; 1]
        """

        self.__computeTrackParams(normedValue)
        currentTrack.num = self.num
        currentTrack.instru = self.instru
        currentTrack.blocDuration = self.blocDuration

        notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages = self.__computeTrackInfo(currentTrack)

        return notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack

    def __resetTrackParams(self, num = None, instru = None, blocDuration = None, tempo = None, volume = None):
        """
        Reset all the track params.
        Should be called at the end of a track creation with all the params to None.

        num : the track number
        instru : the instrument that will play the notes
        blocDuration : the duration of a bloc of notes
        tempo : the tempo of the bloc
        volume : the volume at which the notes will be played
        """
        self.num = num
        self.instru = instru
        self.blocDuration = blocDuration
        self.tempo = tempo
        self.volume = volume

    def setTrackNb(self, trackNb):
        """
        Set the number of track

        trackNb : The number of track
        """
        self.trackNb = trackNb

    def setTrackParams(self, blocDuration, instru = None):
        """
        Set some of the track parameters.

        blocDuration : the duration of each bloc of notes
        instru : the instrument that will play the notes
        """
        self.blocDuration = blocDuration
        self.instru = instru

    def createMidi(self, verbose = False):
        """
        Create the midi file with the created tracks and write the resulting midi file in a folder.

        verbose : True if the info should be printed, False otherwise
        Return : filepath of the mdi file
        """
        self.midi = MIDIFile(self.trackNb)

        trackCounter = 0
        for track in self.tracks:
            blocCounter = 0
            trackCounter += 1
            if verbose:
                print("Track Id : {}".format(trackCounter))
                print("  | Num : {}".format(track.num))
                print("  | Instru : {}".format(track.instru))
                print("  | Bloc duration {}".format(track.blocDuration))
            self.midi.addProgramChange(track.num, 0, 0, track.instru)

            time = 0
            for i, (notes, (noteDuration, tempo)) in enumerate(zip(track.notes, track.blocInfos)):
                blocCounter += 1
                if verbose:
                    print("  | Bloc Id : {}".format(blocCounter))
                    print("    | Note duration : {}".format(noteDuration))
                    print("    | Tempo : {}".format(tempo))
                    print("    | Notes : ", notes)
                
                quarterNoteMultiplier = (tempo / 60)

                noteDuration *= quarterNoteMultiplier
                self.midi.addTempo(track.num, time, tempo)
                
                for note, volume in notes:

                    self.midi.addNote(track.num, 0, note, time, noteDuration, volume)
                    time += noteDuration

        self.midiPath = os.path.join(self.rootPath, 'sounds', self.videoName + '.mid')
        with open(self.midiPath, "wb") as output_file:
            self.midi.writeFile(output_file)

    def random(self, tracks):
        start_time = time.clock()
        self.__printTitle("Random Tracks Algorithm (%d tracks)" % tracks)
        for i in tqdm(range(tracks)):
            track = i
            tempo = random.randint(30, 100)
            notes = []
            for j in range (self.__getNumberNotes(self.clip.duration, tempo)):
                notes.append(random.randint(30, 60))
            self.result.append((track, tempo, notes))
            # self.__printProgress(i + 1, tracks)
        self.__printResult(time.clock() - start_time)

    def diffBetween2Images(self, factor, th = 127, maxNote = 64):
        """
        Create a track based on the track parameters and the differences between two consecutives frame of the video.

        factor :        applied on the note, should be big if the video is generaly quiet,
                            should be low if the video is generaly agitated
        th :            the threshold [0 ; 255]
        maxNote :       max value that can be returned for a note
        """

        # Init vars
        cap = self.videoCap(self.videoName)
        notes = []

        imagesCounter = 0
        imagesCounterTot = 0
        notesCounter = 0
        currentTrack = Track(None, None, None)

        previousNbOfDiff = -1

        if(cap.isOpened()):
            ret, frame = cap.read()

            if(cap.isOpened()):
                previousFrame = frame
                ret, frame = cap.read()
            
                previousNbOfDiff, note = self.__diffBetween2Images(maxNote, factor, previousNbOfDiff, previousFrame, frame, th)

                if(cap.isOpened()):
                    previousFrame = frame
                    ret, frame = cap.read()
                    imagesCounterTot += 3
                    imagesCounter += 3

                    previousNbOfDiff, note = self.__diffBetween2Images(maxNote, factor, previousNbOfDiff, previousFrame, frame, th)
                    normedValue = note / maxNote

                    notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, normedValue)
        
        # For each frame in the video
        pbar = tqdm(total = totNbImgInClip)
        while(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
            pbar.update(1)
            # self.__printProgress(imagesCounterTot, totNbImgInClip)

            if frame is None:
                break
            else:
                if imagesCounter % everyNImages == 0:
                    # Uncomment line bellow to create image
                    #self.__diffBetween2Images_display(previousFrame, frame, th, imagesCounterTot)
                    previousNbOfDiff, note = self.__diffBetween2Images(maxNote, factor, previousNbOfDiff, previousFrame, frame, th)

                    notesCounter += 1
                    notes.append(currentTrack.createNoteVolTuple(note, self.volume))
                
                    # Test if one bloc can be done
                    if notesCounter % notesNbPerBloc == 0:
                        currentTrack.addBlocInfo(noteDuration, self.tempo)
                        currentTrack.addNotes(notes)
                        notes = []
                        notesCounter = 0
                        imagesCounter = 0

                        if(cap.isOpened()):
                            self.__resetTrackParams(self.num, self.instru, self.blocDuration)
                            ret, frame = cap.read()
                            imagesCounterTot += 1
                            imagesCounter += 1
                            
                            previousNbOfDiff, note = self.__diffBetween2Images(maxNote, factor, previousNbOfDiff, previousFrame, frame, th)
                            normedValue = note / maxNote

                            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, normedValue)
        
        if len(notes) > 0:
            currentTrack.addBlocInfo(noteDuration, self.tempo)
            currentTrack.addNotes(notes)

        self.tracks.append(currentTrack)
        self.__resetTrackParams()

    def __diffBetween2Images(self, maxNote, factor, previousNbOfDiff, previousFrame, frame, th):
        
        diff = cv2.absdiff(previousFrame, frame)
        mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        imask = mask > th
        nbOfDiff = np.sum(imask)

        if previousNbOfDiff == -1:
            return nbOfDiff, -1
        else:
            frameSize = np.sum(np.ones_like(frame, np.uint8))
            diffBetweenDiff = np.absolute(nbOfDiff - previousNbOfDiff)
            
            note = int(diffBetweenDiff / frameSize * maxNote * factor)

            if note > maxNote:
                note = maxNote

            return np.sum(imask), note

    def __diffBetween2Images_display(self, previousFrame, frame, th, imgCounter):
        
        diff = cv2.absdiff(previousFrame, frame)
        mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        imask = mask > th

        canvas = np.zeros_like(frame, np.uint8)
        canvas[imask] = frame[imask]

        cv2.imwrite(os.path.join(self.rootPath, "temp", "diffImages", "result" + str(imgCounter) + ".png"), canvas)

    def exemple(self, reduceFrameBy = 100):
        """
        This method is an exemple

        reduceFrameBy :  reduce every frame of the video, if the frame is 1000x1000
                            the resulting frame will be 10x10
        """

        # Init vars
        cap = self.videoCap(self.videoName)
        notes = []

        imagesCounter = 0
        imagesCounterTot = 0
        notesCounter = 0
        currentTrack = Track(None, None, None)

        if(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
        
            # TODO : Prepare and give a normed value with your algo, based on one frame
            normedValue = 0

            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, normedValue)
        
        # For each frame in the video
        pbar = tqdm(total = totNbImgInClip)
        while(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
            pbar.update(1)
            # self.__printProgress(imagesCounterTot, totNbImgInClip)

            if frame is None:
                break
            else:
                if imagesCounter % everyNImages == 0:
                    # TODO : Prepare and give a note, the value of the note should be an int and between [0 ; ~60-70]
                    note = 64

                    notesCounter += 1
                    notes.append(currentTrack.createNoteVolTuple(note, self.volume))
                
                    # Test if one bloc can be done
                    if notesCounter % notesNbPerBloc == 0:
                        currentTrack.addBlocInfo(noteDuration, self.tempo)
                        currentTrack.addNotes(notes)
                        notes = []
                        notesCounter = 0
                        imagesCounter = 0

                        if(cap.isOpened()):
                            self.__resetTrackParams(self.num, self.instru, self.blocDuration)
                            ret, frame = cap.read()
                            imagesCounter += 1
                            
                            # TODO : Prepare and give a normed value with your algo, based on one frame - could be computed like the previous one
                            normedValue = 0

                            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, normedValue)
        
        if len(notes) > 0:
            currentTrack.addBlocInfo(noteDuration, self.tempo)
            currentTrack.addNotes(notes)

        self.tracks.append(currentTrack)
        self.__resetTrackParams()

    def convolution(self, factor, reduceFrameBy = 100, kernel = [[0, 0, 0],[0, 1, 0],[0, 0, 0]]):
        """
        This method is an exemple

        factor :        applied on the note, should be big if the video is generaly smooth,
                            should be low if the video is generaly edgy
        reduceFrameBy :  reduce every frame of the video, if the frame is 1000x1000
                            the resulting frame will be 10x10
        kernel :        2D array specifying the kernel to apply on every frames
        """

        # Init vars
        cap = self.videoCap(self.videoName)
        notes = []

        imagesCounter = 0
        imagesCounterTot = 0
        notesCounter = 0
        currentTrack = Track(None, None, None)

        if(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
        
             # Implementation
            normedValue = self.__applyKernelToFrame(frame, reduceFrameBy, kernel, factor) / 255

            if normedValue > 1:
                normedValue = 1
            if normedValue < 0:
                normedValue = 0

            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, normedValue)
        
        # For each frame in the video
        pbar = tqdm(total = totNbImgInClip)
        while(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
            pbar.update(1)
            # self.__printProgress(imagesCounterTot, totNbImgInClip)

            if frame is None:
                break
            else:
                if imagesCounter % everyNImages == 0:
                    # Implementation
                    note = int(self.__applyKernelToFrame(frame, reduceFrameBy, kernel, factor) / 4)

                    notesCounter += 1
                    notes.append(currentTrack.createNoteVolTuple(note, self.volume))
                
                    # Test if one bloc can be done
                    if notesCounter % notesNbPerBloc == 0:
                        currentTrack.addBlocInfo(noteDuration, self.tempo)
                        currentTrack.addNotes(notes)
                        notes = []
                        notesCounter = 0
                        imagesCounter = 0

                        if(cap.isOpened()):
                            self.__resetTrackParams(self.num, self.instru, self.blocDuration)
                            ret, frame = cap.read()
                            imagesCounter += 1
                            
                             # Implementation
                            normedValue = self.__applyKernelToFrame(frame, reduceFrameBy, kernel, factor) / 255

                            if normedValue > 1:
                                normedValue = 1
                            if normedValue < 0:
                                normedValue = 0

                            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, normedValue)
        
        if len(notes) > 0:
            currentTrack.addBlocInfo(noteDuration, self.tempo)
            currentTrack.addNotes(notes)

        self.tracks.append(currentTrack)
        self.__resetTrackParams()

    def __applyKernelToFrame(self, frame, reduceFrameBy, kernel, factor):
        kernelRadius = int(len(kernel) / 2)
        frameW = int(len(frame) / reduceFrameBy)
        frameH = int(len(frame[0]) / reduceFrameBy)
        result = 0

        for i in range(kernelRadius, frameW - kernelRadius):
            for j in range(kernelRadius, frameW - kernelRadius):
                sum = 0
                for m in range(-kernelRadius, kernelRadius):
                    for n in range(-kernelRadius, kernelRadius):
                        sum += frame[i + m][j + n] * kernel[m + kernelRadius + 1][n + kernelRadius + 1]
                result += int((sum[0] + sum[1] + sum[2]) / 3)
        n = frameW * frameH
        return int((result * factor) / n)

    def averageRGB(self, reduceFrameBy = 100):
        """
        Create a track based on the track parameters and the average color of the video.

        reduceFrameBy :  reduce every frame of the video, if the frame is 1000x1000
                            the resulting frame will be 10x10
        """

        # Init vars
        cap = self.videoCap(self.videoName)
        notes = []

        imagesCounter = 0
        imagesCounterTot = 0
        notesCounter = 0
        currentTrack = Track(None, None, None)

        if(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
        
            averageR = self.__averageRGBChoiceOneFrame(frame, 0, reduceFrameBy)
            averageG = self.__averageRGBChoiceOneFrame(frame, 1, reduceFrameBy)
            averageB = self.__averageRGBChoiceOneFrame(frame, 2, reduceFrameBy)
            averageRGBNorm = (averageR + averageG + averageB) / 3 / 255

            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, averageRGBNorm)
        
        # For each frame in the video
        pbar = tqdm(total = totNbImgInClip)
        while(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
            pbar.update(1)
            # self.__printProgress(imagesCounterTot, totNbImgInClip)

            if frame is None:
                break
            else:
                if imagesCounter % everyNImages == 0:
                    averageR = self.__averageRGBChoiceOneFrame(frame, 0, reduceFrameBy)
                    averageG = self.__averageRGBChoiceOneFrame(frame, 1, reduceFrameBy)
                    averageB = self.__averageRGBChoiceOneFrame(frame, 2, reduceFrameBy)
                    note = int((averageR + averageG + averageB) / 3 / 4)

                    notesCounter += 1
                    notes.append(currentTrack.createNoteVolTuple(note, self.volume))
                
                    # Test if one bloc can be done
                    if notesCounter % notesNbPerBloc == 0:
                        currentTrack.addBlocInfo(noteDuration, self.tempo)
                        currentTrack.addNotes(notes)
                        notes = []
                        notesCounter = 0
                        imagesCounter = 0

                        if(cap.isOpened()):
                            self.__resetTrackParams(self.num, self.instru, self.blocDuration)
                            ret, frame = cap.read()
                            imagesCounter += 1
        
                            averageR = self.__averageRGBChoiceOneFrame(frame, 0, reduceFrameBy)
                            averageG = self.__averageRGBChoiceOneFrame(frame, 1, reduceFrameBy)
                            averageB = self.__averageRGBChoiceOneFrame(frame, 2, reduceFrameBy)
                            averageRGBNorm = (averageR + averageG + averageB) / 3 / 255

                            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, averageRGBNorm)
        
        if len(notes) > 0:
            currentTrack.addBlocInfo(noteDuration, self.tempo)
            currentTrack.addNotes(notes)

        self.tracks.append(currentTrack)
        self.__resetTrackParams()

    def averageRGBChannel(self, colorChannel, reduceFrameBy = 100):
        """
        Create a track based on the track parameters and the average red, green or blue color of the video.

        reduceFrameBy :  reduce every frame of the video, if the frame is 1000x1000
                            the resulting frame will be 10x10
        colorChannel :      0 = blue, 1 = green, 2 = red
        """

        # Init vars
        cap = self.videoCap(self.videoName)
        notes = []

        imagesCounter = 0
        imagesCounterTot = 0
        notesCounter = 0
        currentTrack = Track(None, None, None)

        if(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1

            averageChannelNorm = self.__averageRGBChoiceOneFrame(frame, colorChannel, reduceFrameBy) / 255
            
            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, averageChannelNorm)
        
        # For each frame in the video
        pbar = tqdm(total = totNbImgInClip)
        while(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
            pbar.update(1)
            # self.__printProgress(imagesCounterTot, totNbImgInClip)

            if frame is None:
                break
            else:
                if imagesCounter % everyNImages == 0:
                    note = int(self.__averageRGBChoiceOneFrame(frame, colorChannel, reduceFrameBy) / 4)

                    notesCounter += 1
                    notes.append(currentTrack.createNoteVolTuple(note, self.volume))
                
                    # Test if one bloc can be done
                    if notesCounter % notesNbPerBloc == 0:
                        currentTrack.addBlocInfo(noteDuration, self.tempo)
                        currentTrack.addNotes(notes)
                        notes = []
                        notesCounter = 0
                        imagesCounter = 0

                        if(cap.isOpened()):
                            self.__resetTrackParams(self.num, self.instru, self.blocDuration)
                            ret, frame = cap.read()
                            imagesCounter += 1
                            
                            averageChannelNorm = self.__averageRGBChoiceOneFrame(frame, colorChannel, reduceFrameBy) / 255

                            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__computeTrack(currentTrack, averageChannelNorm)
        
        if len(notes) > 0:
            currentTrack.addBlocInfo(noteDuration, self.tempo)
            currentTrack.addNotes(notes)

        self.tracks.append(currentTrack)
        self.__resetTrackParams()

    def __averageRGBChoiceOneFrame(self, frame, colorChannel, reduceFrameBy):
        """
        Compute a note between [0 ; 255] based on the average of
        red, green or blue in a given frame.

        frame :             the images
        colorChannel :      0 = red, 1 = green, 2 = blue
        reduceFrameBy :  reduce every frame of the video, if the frame is 1000x1000
                            the resulting frame will be 10x10
        """

        vect = frame.shape
        dimX = vect[0]
        dimY = vect[1]

        averageColor = 0
        pixelsNb = 0
        for x in range(0, dimX, reduceFrameBy):
            for y in range(0, dimY, reduceFrameBy):
                averageColor += frame[x][y][colorChannel]
                pixelsNb += 1

        averageColor /= pixelsNb

        return averageColor

    def videoCap(self, videoName):
        """
        Create a capture based on the given video name.
        The video should be placed in the video folder in order to found.

        videoName : the name of the video
        """
        cap = cv2.VideoCapture(self.videoPath)
        return cap

    def convertMdiToMp3(self):
        if self.midiPath == None:
            print("Impossible to convert the midi file because it doesn't exist. Please call the createMidi() function before calling this one.")
            return
        try:
            mdiName = self.midiPath.replace("/", "\\")
            savePath = os.path.join(self.rootPath, "sounds")

            timeoutDelay = 60   # wait for 60 seconds
            filename = os.path.splitext(os.path.basename(mdiName))[0] + ".mp3"

            options = Options()
            options.headless = True

            # Set firefox parameters to download easily the file
            profile = webdriver.FirefoxProfile()
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.manager.showWhenStarting", False)

            profile.set_preference("browser.download.dir", savePath)
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mpeg")

            # Check if the file already exist, if so, remove it
            if os.path.exists(os.path.join(savePath, filename)):
                os.remove(os.path.join(savePath, filename))

            # Go to the site and download the file
            geckodriverPath = os.path.join(self.rootPath, "libs", "geckodriver", "geckodriver.exe")
            driver = webdriver.Firefox(options=options, executable_path=geckodriverPath, firefox_profile=profile)
            driver.get('https://www.onlineconverter.com/midi-to-mp3')
            driver.find_element_by_id("file").send_keys(os.path.join(self.rootPath, mdiName))
            driver.find_element_by_id('convert-button').click()

            print("Converting the midi file to mp3...", flush=True)
            # Wait until the file is downloaded
            while not os.path.exists(os.path.join(savePath, filename)) and timeoutDelay > 0:
                time.sleep(1)
                timeoutDelay -= 1

            if os.path.exists(os.path.join(savePath, filename)):
                # Move the file to the current directory
                # movedPath = os.path.join(os.getcwd(), "sounds", filename)
                # shutil.move(os.path.join(savePath, filename), movedPath)

                self.mp3Path = os.path.join(savePath, filename)
            else:
                print("Could not convert the midi file to mp3")
        except:
            print("Impossible to connect to the site in order to convert the file. Make sure Firefox is installed.")

    def addMp3ToAvi(self):
        if self.mp3Path == None:
            print("Impossible to create the avi file because the mp3 file doesn't exist. Please call the convertMdiToMp3() function before calling this one.")
            return

        input("Press Enter when the mp3 file has been copied to the sounds folder...")

        print("Creation of the video file...")

        try:
            inputs = OrderedDict([(self.videoPath, None), (self.mp3Path, None)])
            outputs = {self.videoName + '.avi': '-hide_banner -loglevel panic -map 0:v -map 1:a -c copy -shortest -y'}
            ff = FFmpeg(executable=os.path.join(self.rootPath, 'libs', 'ffmpeg', 'bin', 'ffmpeg.exe'), inputs=inputs, outputs=outputs)
            
            ff.run()

            shutil.move(os.path.join(self.rootPath, self.videoName + '.avi'), os.path.join(self.rootPath, 'outputs', self.videoName + '.avi'))

            print("Creation of the avi file complete. You can find it under the outputs folder.")
        except Exception as e: 
            print(e)
            # print("Error while creating the video")
