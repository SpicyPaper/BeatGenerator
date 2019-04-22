
from Generator import Generator
from Track import Track
from MDItoMP3 import convertMdiToMp3
from addMp3ToAvi import addMp3ToAvi

if __name__ == "__main__":
    
    gen = Generator("Fond_Noir_Tissu_Cam_Fixe_2")
    gen.setTrackParams(3, 12)
    gen.averageRGB()
    mdiPath = gen.createMidi(True)
    mp3Path = convertMdiToMp3(mdiPath)
    addMp3ToAvi("Videos/Fond_Noir_Tissu_Cam_Fixe_2.avi", mp3Path)