import numpy as np
import argparse
from moviepy.video.io.VideoFileClip import VideoFileClip
from Generator import Generator

if __name__ == "__main__":

    clip = VideoFileClip("Class_Room_Tour.avi")
    gen = Generator(clip)
    gen.random(4)
    MIDI = gen.getMIDI()

    with open("major-scale.mid", "wb") as output_file:
        MIDI.writeFile(output_file)