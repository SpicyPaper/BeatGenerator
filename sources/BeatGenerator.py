
from Generator import Generator
from Track import Track
from MDItoMP3 import convertMdiToMp3
from addMp3ToAvi import addMp3ToAvi
if __name__ == "__main__":
    
    gen = Generator("Class_Room_Tour")

    """gen.setTrackParams(3)
    gen.averageRGB()
    gen.setTrackParams(3)
    gen.diffBetween2Images(100)
    gen.setTrackParams(3)
    gen.averageRGBChannel(0)
    gen.setTrackParams(3)
    gen.averageRGBChannel(1)
    gen.setTrackParams(3)
    gen.averageRGBChannel(2)"""

    gen.setTrackParams(3, 12)
    gen.convolution(10, [[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]])
    gen.createMidi(True)
    gen.convertMdiToMp3()
    gen.addMp3ToAvi()