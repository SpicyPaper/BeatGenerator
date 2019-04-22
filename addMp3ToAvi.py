from ffmpy import FFmpeg
from collections import OrderedDict

def addMp3ToAvi(videoFileName, audioFileName):

    inputs = OrderedDict([(videoFileName, None), (audioFileName, None)])
    outputs = {'output.avi': '-map 0:v -map 1:a -c copy -shortest -y'}
    ff = FFmpeg(inputs=inputs, outputs=outputs)
    
    ff.run()