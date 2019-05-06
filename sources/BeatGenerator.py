
from Generator import Generator
from Track import Track

if __name__ == "__main__":
    
    gen = Generator("Edges_2")
    gen.setTrackParams(0.5, 12)
    gen.convolution(1, everyNPixels = 10, kernel = [[1, 0, -1],[1, 0, -1],[1, 0, -1]])
    gen.createMidi(True)
    gen.convertMdiToMp3()
    gen.addMp3ToAvi()
