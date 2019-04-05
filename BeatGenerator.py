
from Generator import Generator
from Track import Track

if __name__ == "__main__":
    
    gen = Generator("Class_Room_Tour")
    gen.averageRGB()
    MIDI = gen.getMIDI()

    for track in gen.tracks:
        MIDI.addProgramChange(track.num, 0, 0, track.instru)

        for i, (notes, (noteDuration, tempo)) in enumerate(zip(track.notes, track.blocInfos)):
            
            quarterNoteMultiplier = (tempo / 60)

            time = track.blocDuration * i
            MIDI.addTempo(track.num, time * quarterNoteMultiplier, tempo)
            
            for note, volume in notes:
                MIDI.addNote(track.num, 0, note, time * quarterNoteMultiplier, noteDuration * quarterNoteMultiplier, volume)
                print(time)
                time += noteDuration

    with open('Sounds/' + gen.videoName + '.mid', "wb") as output_file:
        MIDI.writeFile(output_file)
    
    # Alex part
    """
    # -- Init
    degrees = []
    maxSound = 60
    videoName = 'Class_Room_Tour'

    # -- Apply algo on video
    #degrees = diffBetween2Images(videoName, maxSound, 1000, 10, 120)
    degrees = averageRGB(videoName, 100, 10)
    #degrees = averageRGBChannel(videoName, 100, 10, 0)
    print(degrees)

    # -- Create the music based on previous info
    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 170   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    # Get the duration of the video
    clip = VideoFileClip('Videos/' + videoName + '.avi')
    print( clip.duration )  
    # Define the number of note the music must have according to the tempo
    numberOfNote = getNumberNote(clip.duration, tempo)

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                        # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    with open('Sounds/' + videoName + '.mid', "wb") as output_file:
        MyMIDI.writeFile(output_file)
    """
    # Etienne part
    """
    clip = VideoFileClip("Class_Room_Tour.avi")
    gen = Generator(clip)
    gen.random(4)
    MIDI = gen.getMIDI()

    with open("major-scale.mid", "wb") as output_file:
        MIDI.writeFile(output_file)
    """