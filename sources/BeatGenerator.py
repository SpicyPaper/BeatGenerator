
from Generator import Generator
from Track import Track
from MDItoMP3 import convertMdiToMp3
from addMp3ToAvi import addMp3ToAvi
if __name__ == "__main__":
    
    gen = Generator("Class_Room_Tour")

    gen.setTrackParams(0.5)
    gen.diffBetween2Images(100, 127, 64)
    gen.createMidi(True)
    gen.convertMdiToMp3()
    gen.addMp3ToAvi()