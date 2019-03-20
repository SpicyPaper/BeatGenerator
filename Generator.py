import sys
import random
import time
from midiutil import MIDIFile

class Generator:
    
    def __init__(self, clip):
        self.result = []
        self.clip = clip;

    def __printTitle(self, algoName):
        print("     ____             __     ______                           __            ")
        print("    / __ )___  ____ _/ /_   / ____/__  ____  ___  _________ _/ /_____  _____")
        print("   / __  / _ \/ __ `/ __/  / / __/ _ \/ __ \/ _ \/ ___/ __ `/ __/ __ \/ ___/")
        print("  / /_/ /  __/ /_/ / /_   / /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /    ")
        print(" /_____/\___/\__,_/\__/   \____/\___/_/ /_/\___/_/   \__,_/\__/\____/_/     ")
        print("\n                                                 Traitement d'image - 2019")
        print("\n  Using:", algoName);

    def __printProgress(self, current, max):
        progress = int(100 * current / max)
        current = int(progress / 2)
        print(" [", end='')
        for i in range (current):
            print("=", end='')
        for i in range (50 - current):
            print(" ", end='')
        print("]", end='')

        if (progress < 100):
            print(" %d" % progress, "%", end='\r')
        else:
            print(" %d" % progress, "%")

    def __printResult(self, time):
        print("  Time taken: %d" % time, "second(s)")

    def __getNumberNotes(self, musicDuration, tempo):
        durationInMinute = musicDuration / 60
        return int(tempo * durationInMinute)

    def random(self, tracks):
        start_time = time.clock()
        self.__printTitle("Random Tracks Algorithm (%d tracks)" % tracks)
        for i in range(tracks):
            track = i
            tempo = random.randint(30, 100)
            notes = []
            for j in range (self.__getNumberNotes(self.clip.duration, tempo)):
                notes.append(random.randint(30, 60))
            self.result.append((track, tempo, notes))
            self.__printProgress(i + 1, tracks)
        self.__printResult(time.clock() - start_time)

    def getMIDI(self):
        nb_tracks = len(self.result)
        MIDI = MIDIFile(nb_tracks)

        j = 0
        for track, tempo, notes in self.result:
            MIDI.addTempo(track, 0, tempo)
            for i, note in enumerate(notes):
                MIDI.addProgramChange(track, i, i, 109 + j)
                MIDI.addNote(track, i, note, i, 1, 100)
            j += 1
        
        return MIDI