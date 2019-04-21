
from Generator import Generator
from Track import Track

if __name__ == "__main__":
    
    gen = Generator("Class_Room_Tour")
    gen.setTrackParams(3, 12)
    gen.averageRGB()
    gen.createMidi(True)