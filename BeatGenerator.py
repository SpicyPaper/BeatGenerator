
from Generator import Generator
from Track import Track
from MDItoMP3 import convertMdiToMp3
from addMp3ToAvi import addMp3ToAvi

if __name__ == "__main__":
    
    gen = Generator("Class_Room_Tour")
    gen.setTrackParams(3, 12)
    gen.averageRGB()
    mdiPath = gen.createMidi(True)
    mp3Path = convertMdiToMp3(mdiPath)
    addMp3ToAvi("Videos/Class_Room_Tour.avi", mp3Path)