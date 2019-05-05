
from Generator import Generator
from Track import Track

if __name__ == "__main__":
    
    gen = Generator("Chillys_Bottle_Fix_Cam")

    gen.setTrackParams(0.5, 12)
    gen.averageRGB()
    gen.createMidi()
    gen.convertMdiToMp3()
    gen.addMp3ToAvi()