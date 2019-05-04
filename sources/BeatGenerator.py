
from Generator import Generator
from Track import Track

if __name__ == "__main__":
    
    gen = Generator("Fond_Noir_Tissu_Cam_Fixe_2")

    gen.setTrackParams(0.5, 12)
    # gen.convolution(10, [[1, 0, -1],[1, 0, -1],[1, 0, -1]])
    gen.averageRGB()
    gen.createMidi(True)
    gen.convertMdiToMp3()
    gen.addMp3ToAvi()