
from Generator import Generator
from Track import Track

if __name__ == "__main__":
    
    gen = Generator("RGBW")
    gen.setTrackParams(0.5, 12)
    gen.averageRGB()
    gen.createMidi(True)
    gen.convertMdiToMp3()
    gen.addMp3ToAvi()