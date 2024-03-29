class Track:
	
    def __init__(self, num, instru, blocDuration):
        self.num = num
        self.instru = instru
        self.blocDuration = blocDuration
        
        self.blocInfos = []
        self.notes = []
    
    def addBlocInfo(self, noteDuration, tempo):
        self.blocInfos.append( ( noteDuration, tempo) )

    def addNotes(self, notes):
        """

        notes : array of tuple (note, volume)
        """
        self.notes.append(notes)

    def createNoteVolTuple(self, note, volume):
        return (note, volume)
        