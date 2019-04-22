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

    mdiName = mdiName.replace("/", "\\")
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

    print("Converting the file...", flush=True)
    # Wait until the file is downloaded
    while not os.path.exists(os.path.join(savePath, filename)) and timeoutDelay > 0:
        time.sleep(1)
        timeoutDelay -= 1

    # Move the file to the current directory
    movedPath = os.path.join(os.getcwd(), filename)
    shutil.move(os.path.join(savePath, filename), movedPath)

    return os.path.basename(movedPath)

