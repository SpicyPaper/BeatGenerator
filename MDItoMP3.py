from midiutil import MIDIFile
import numpy as np
import cv2
import sys
import argparse
import random
import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from moviepy.video.io.VideoFileClip import VideoFileClip

def convertMdiToMp3(mdiName):

    timeoutDelay = 30   # wait for 30 seconds
    filename = os.path.splitext(mdiName)[0] + ".mp3"

    # options = Options()
    # options.headless = False

    # # Set firefox parameters to download easily the file
    # profile = webdriver.FirefoxProfile()
    # profile.set_preference("browser.download.folderList", 2)
    # profile.set_preference("browser.download.manager.showWhenStarting", False)
    # print(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))

    savePath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

    # profile.set_preference("browser.download.dir", savePath)
    # profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mpeg")

    # # Go to the site and download the file
    # driver = webdriver.Firefox(options=options, executable_path=r'geckodriver.exe', firefox_profile=profile)
    # driver.get('https://www.onlineconverter.com/midi-to-mp3')
    # driver.find_element_by_id("file").send_keys(os.path.join(os.getcwd(), mdiName))
    # driver.find_element_by_id('convert-button').click()


    print("Converting the file..." flush=True)
    # Wait until the file is downloaded
    while not os.path.exists(os.path.join(savePath, filename)) and timeoutDelay > 0:
        time.sleep(1)
        timeoutDelay -= 1

    # Move the file to the current directory
    shutil.move(os.path.join(savePath, filename), os.path.join(os.getcwd(), filename))

    


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

    # while(cap.isOpened()):
    #     ret, frame = cap.read()
    #     everyNImages = 10

    #     if frame is None:
    #         break
    #     else:
    #         if counter % everyNImages == 0:
    #             degrees.append(averageRGB(frame, 100))
    #         counter += 1

    # cap.release()
    # cv2.destroyAllWindows()

    

    # Get the duration of the video
    clip = VideoFileClip("Class_Room_Tour.avi")
    

    MyMIDI = MIDIFile(2)  # One track, defaults to format 1 (tempo track is created
                        # automatically)
    
    multiple_tempo_test(0, 0, 60, 4, MyMIDI, clip.duration)
    multiple_tempo_test(1, 1, 80, 109, MyMIDI, clip.duration)
    

    with open("music.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)

    convertMdiToMp3("music.mid")

