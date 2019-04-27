import argparse
import os
import random
import shutil
import sys
import time
from collections import OrderedDict
import math

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
        
        self.rootPath = os.path.dirname(sys.argv[0])
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
                self.lastTrackNum

        if self.instru == None:
            self.instru = int(usedNormedValue * 127)

        if self.blocDuration == None:
            self.blocDuration = blocDuration

        if self.tempo == None:
            self.tempo = int(usedNormedValue * 180)

        if self.volume == None:
            self.volume = volume

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

    def setTrackParams(self, blocDuration, instru = None, trackNb = 5):
        """
        Set some of the track parameters.

        blocDuration : the duration of each bloc of notes
        instru : the instrument that will play the notes
        trackNb : the number of available tracks
        """
        self.blocDuration = blocDuration
        self.instru = instru
        self.trackNb = trackNb

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

        self.midiPath = os.path.join(self.rootPath, 'Sounds', self.videoName + '.mid')
        with open(self.midiPath, "wb") as output_file:
            self.midi.writeFile(output_file)

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
        notes = []  # MIDI note number
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
                        notes.append(sound)
                counter += 1

        return notes

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

        cv2.imwrite(os.path.join(self.rootPath, "DiffImages", "result" + str(imgCounter) + ".png"), canvas)

    def averageRGB(self, everyNPixels = 100):
        """
        Create a track based on the track parameters and the average color of the video.

        everyNPixels : takes one pixel every N pixels
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
            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__averageRGBComputeTrack(frame, everyNPixels, currentTrack)
        
        # For each frame in the video
        while(cap.isOpened()):
            ret, frame = cap.read()
            imagesCounterTot += 1
            imagesCounter += 1
            self.__printProgress(imagesCounterTot, totNbImgInClip)

            if frame is None:
                break
            else:
                if imagesCounter % everyNImages == 0:
                    averageR = self.__averageRGBChoiceOneFrame(frame, 0, everyNPixels)
                    averageG = self.__averageRGBChoiceOneFrame(frame, 1, everyNPixels)
                    averageB = self.__averageRGBChoiceOneFrame(frame, 2, everyNPixels)

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
                            notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack = self.__averageRGBComputeTrack(frame, everyNPixels, currentTrack)

        if len(notes) > 0:
            currentTrack.addBlocInfo(noteDuration, self.tempo)
            currentTrack.addNotes(notes)

        self.tracks.append(currentTrack)
        self.__resetTrackParams()

    def __averageRGBComputeTrack(self, frame, everyNPixels, currentTrack):
        """
        Update track parameters based on a frame of the video.

        frame : a frame of the video
        everyNPixels : takes one pixel every N pixels
        currentTrack : the track that should be update
        """
        
        averageR = self.__averageRGBChoiceOneFrame(frame, 0, everyNPixels)
        averageG = self.__averageRGBChoiceOneFrame(frame, 1, everyNPixels)
        averageB = self.__averageRGBChoiceOneFrame(frame, 2, everyNPixels)

        averageRGBNorm = (averageR + averageG + averageB) / 3 / 255

        self.__computeTrackParams(averageRGBNorm)
        currentTrack.num = self.num
        currentTrack.instru = self.instru
        currentTrack.blocDuration = self.blocDuration

        notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages = self.__computeTrackInfo(currentTrack)

        return notesNbPerBloc, noteDuration, totNbImgInClip, everyNImages, currentTrack

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
        notes = []  # MIDI note number
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
                    notes.append(averageColorChannel)

        return notes

    def __averageRGBChoiceOneFrame(self, frame, colorChannel, everyNPixels):
        """
        Compute a sound between [0 ; 255] based on the average of
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
        everyNPixels = int(math.sqrt(everyNPixels))

        averageColor = cv2.mean(frame[:, :, colorChannel])
        # for x in range(0, dimX, everyNPixels):
        #     for y in range(0, dimY, everyNPixels):
        #         averageColor += frame[x][y][colorChannel]
        #         nbPixels += 1

        # [0 ; 255]
        # averageColor = int(averageColor / nbPixels)

        return averageColor[0]

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
            savePath = os.path.join(os.environ['USERPROFILE'], 'Desktop')

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

            # Go to the site and download the file
            driver = webdriver.Firefox(options=options, executable_path=r'geckodriver.exe', firefox_profile=profile)
            driver.get('https://www.onlineconverter.com/midi-to-mp3')
            driver.find_element_by_id("file").send_keys(os.path.join(os.getcwd(), mdiName))
            driver.find_element_by_id('convert-button').click()

            print("Converting the midi file to mp3...", flush=True)
            # Wait until the file is downloaded
            while not os.path.exists(os.path.join(savePath, filename)) and timeoutDelay > 0:
                time.sleep(1)
                timeoutDelay -= 1

            if os.path.exists(os.path.join(savePath, filename)):
                # Move the file to the current directory
                movedPath = os.path.join(os.getcwd(), filename)
                shutil.move(os.path.join(savePath, filename), movedPath)

                self.mp3Path = os.path.basename(movedPath)
            else:
                print("Could not convert the midi file to mp3")
        except:
            print("Impossible to connect to the site in order to convert the file. Make sure Firefox is installed.")

    def addMp3ToAvi(self):
        if self.mp3Path == None:
            print("Impossible to create the avi file because the mp3 file doesn't exist. Please call the convertMdiToMp3() function before calling this one.")
            return

        print("Creation of the video file...")

        try:
            inputs = OrderedDict([(self.videoPath, None), (self.mp3Path, None)])
            outputs = {'output.avi': '-hide_banner -loglevel panic -map 0:v -map 1:a -c copy -shortest -y'}
            ff = FFmpeg(executable=os.path.join(self.rootPath, 'ffmpeg', 'bin', 'ffmpeg.exe'), inputs=inputs, outputs=outputs)
            
            ff.run()

            shutil.move(os.path.join(self.rootPath, 'output.avi'), os.path.join(self.rootPath, 'Outputs', 'output.avi'))

            print("Creation of the avi file complete. You can find it under the Outputs folder.")
        except:
            print("Error while creating the video")
