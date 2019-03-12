from midiutil import MIDIFile
import numpy as np
import cv2
import sys
import argparse
import random
from moviepy.video.io.VideoFileClip import VideoFileClip

imgCounter = 1

def diffBetween2Images(previousFrame, frame, th):
    
    diff = cv2.absdiff(previousFrame, frame)
    mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    imask = mask > th

    canvas = np.zeros_like(frame, np.uint8)
    canvas[imask] = frame[imask]

    global imgCounter
    cv2.imwrite("Diff/result" + str(imgCounter) + ".png", canvas)
    imgCounter += 1

def main_diffBetween2Images(cap, th):

    degrees = []  # MIDI note number
    counter = 0

    if(cap.isOpened()):
        ret, frame = cap.read()
    
    while(cap.isOpened()):
        previousFrame = frame
        ret, frame = cap.read()
        everyNImages = 1

        if frame is None:
            break
        else:
            if counter % everyNImages == 0:
                #degrees.append(averageRGB(frame, 100))
                degrees.append(diffBetween2Images(previousFrame, frame, th))
            counter += 1

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

    videoNameTMP = 'Videos/Fond_Noir_Tissu_Cam_Fixe'

    cap = cv2.VideoCapture(videoNameTMP + '.avi')

    main_diffBetween2Images(cap, 5)

    cap.release()
    cv2.destroyAllWindows()

    # track    = 0
    # channel  = 0
    # time     = 0    # In beats
    # duration = 1    # In beats
    # tempo    = 50   # In BPM
    # volume   = 100  # 0-127, as per the MIDI standard

    # # Get the duration of the video
    # clip = VideoFileClip(videoNameTMP + '.avi')
    # print( clip.duration )  
    # # Define the number of note the music must have according to the tempo
    # numberOfNote = getNumberNote(clip.duration, tempo)

    # # Generate the correct number of note to have a music of the desired length
    # for i in range(numberOfNote):
    #     degrees.append(random.randint(10, 100))

    # MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
    #                     # automatically)
    # MyMIDI.addTempo(track, time, tempo)

    # for i, pitch in enumerate(degrees):
    #     MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    # with open(videoNameTMP + '.mid', "wb") as output_file:
    #     MyMIDI.writeFile(output_file)
