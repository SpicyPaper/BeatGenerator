from midiutil import MIDIFile
import numpy as np
import cv2
import sys
import argparse
import random
from moviepy.video.io.VideoFileClip import VideoFileClip

def diffBetween2Images(cap, everyNImages, th):

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
                previousNbOfDiff, sound = __diffBetween2Images(previousNbOfDiff, previousFrame, frame, th)
                if sound != -1:
                    degrees.append(sound)
            counter += 1

    return degrees

def __diffBetween2Images(previousNbOfDiff, previousFrame, frame, th):
    
    diff = cv2.absdiff(previousFrame, frame)
    mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    imask = mask > th
    nbOfDiff = np.sum(imask)

    if previousNbOfDiff == -1:
        return nbOfDiff, -1
    else:
        frameSize = np.sum(np.ones_like(frame, np.uint8))
        diffBetweenDiff = np.absolute(nbOfDiff - previousNbOfDiff)
        
        sound = int(diffBetweenDiff / frameSize * 60)

        return np.sum(imask), sound

def __diffBetween2Images_display(previousFrame, frame, th, imgCounter):
    
    diff = cv2.absdiff(previousFrame, frame)
    mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    imask = mask > th

    canvas = np.zeros_like(frame, np.uint8)
    canvas[imask] = frame[imask]

    cv2.imwrite("DiffImages/result" + str(imgCounter) + ".png", canvas)

def averageRGB(cap, everyNPixels, everyNImages):
    """
    Compute the average color of a given video
    """

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
                averageR = __averageRGBChoiceOneFrame(frame, 0, everyNPixels)
                averageG = __averageRGBChoiceOneFrame(frame, 1, everyNPixels)
                averageB = __averageRGBChoiceOneFrame(frame, 2, everyNPixels)

                averageColor = int((averageR + averageG + averageB) / 3)

                degrees.append(averageColor)

    return degrees

def averageRGBStage(cap, everyNPixels, everyNImages, colorStage):
    """
    Compute the average color of a given video
    """

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
                averageStage = __averageRGBChoiceOneFrame(frame, colorStage, everyNPixels)
                degrees.append(averageStage)

    return degrees

def __averageRGBChoiceOneFrame(frame, colorStage, everyNPixels):
    """
    Compute a sound between [0 ; 255 / 4] based on the average of
    red, green or blue in a given frame.

    frame : the images
    colorStage : 0 = red, 1 = green, 2 = blue
    everyNPixels : take one pixel every n pixels
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

    """Init"""
    degrees = []
    videoName = 'Fond_Noir_Tissu_Cam_Fixe_Start_Part'
    cap = cv2.VideoCapture('Videos/' + videoName + '.avi')

    """Apply algo on video"""
    degrees = diffBetween2Images(cap, 10, 120)
    print(degrees)
    #degrees = averageRGB(cap, 100, 10)
    #degrees = averageRGBStage(cap, 100, 10, 0)

    """Release"""
    cap.release()

    """Create the music based on previous info"""
    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 50   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    # Get the duration of the video
    clip = VideoFileClip('Videos/' + videoName + '.avi')
    print( clip.duration )  
    # Define the number of note the music must have according to the tempo
    numberOfNote = getNumberNote(clip.duration, tempo)

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                        # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    with open('Sounds/' + videoName + '.mid', "wb") as output_file:
        MyMIDI.writeFile(output_file)
