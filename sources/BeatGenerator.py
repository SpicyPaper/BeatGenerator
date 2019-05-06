
from Generator import Generator
from Track import Track

if __name__ == "__main__":
    
    gen = Generator("Edges_2")
    gen.convolution(factor = 1, everyNPixels = 100, kernel = [[1, 0, -1],[1, 0, -1],[1, 0, -1]])
    gen.createMidi(True)
    gen.convertMdiToMp3()
    gen.addMp3ToAvi()