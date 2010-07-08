import music21.chord
import music21.interval
import pdb

ILLEGAL_INTERVALS = [1]

def fromNotes(stream):
	""" Creates a chord progression guessed from a sequence of notes.
	
	>>> from music21 import note
	>>> from music21 import stream
	>>> s = stream.Stream()
	>>> s.append(note.Note('G', type = 'half'))
	>>> s.append(note.Note('B', type = 'quarter'))
	>>> s.append(note.Note('D', type = 'quarter'))
	>>> s.append(note.Note('G#', type = 'half'))
	>>> s.append(note.Note('C', type = 'quarter'))
	>>> s.append(note.Note('D#', type = 'quarter'))
	>>> cp = fromNotes(s)
	>>> str(cp)
	'G   G#  '
	"""
	cp = ChordProgression()
	
	noteStream = stream.flat.notes
	totalBeats = noteStream.duration.quarterLength
	
	beatPos = 0
	
	while beatPos < totalBeats:
		quarterLenBeats = 8
		while quarterLenBeats > 1:
			guessedChord = _findChord(
				noteStream.getElementsByOffset(beatPos, beatPos + quarterLenBeats, False)
			)
			if guessedChord:
				cp.addChordAt(guessedChord, beatPos)
				beatPos += quarterLenBeats
				break
			quarterLenBeats /= 2
	
	return cp

def _findChord(noteStream):
	""" Guess chord from a stream of notes.
	
	>>> from music21 import note
	>>> from music21 import stream
	>>> s = stream.Stream()
	>>> s.append(note.Note('G#', type = 'half'))
	>>> s.append(note.Note('C', type = 'quarter'))
	>>> s.append(note.Note('D#', type = 'quarter'))
	>>> _findChord(s)
	'G#'
	>>> s = stream.Stream()
	
	Now testing a minor chord.
	>>> s.append(note.Note('G#', type = 'half'))
	>>> s.append(note.Note('C-', type = 'quarter'))
	>>> s.append(note.Note('D#', type = 'quarter'))
	>>> _findChord(s)
	'G#m'
	"""
	found = music21.chord.Chord(noteStream)
	rootPitch = found.root()
	
	if not rootPitch:
		return None
	
	minority = ''
	
	rootPitchClass = rootPitch.pitchClass
	pitchClasses = [pitch.pitchClass for pitch in found.pitches]
	
	for pitchClass in pitchClasses:
		if _isIllegal(rootPitchClass, pitchClass):
			return None
		if (rootPitchClass + 3) % 12 == pitchClass:
			minority = 'm'
	return rootPitch.name + minority

def _isIllegal(pitchClassA, pitchClassB):
	""" Checks whether interval is illegal.
	
	>>> _isIllegal(0, 1)
	True
	>>> _isIllegal(1, 0)
	True
	>>> _isIllegal(10, 11)
	True
	>>> _isIllegal(11, 10)
	True
	"""
	if pitchClassA > pitchClassB:
		for interval in ILLEGAL_INTERVALS:
			if (pitchClassB + interval) % 12 == pitchClassA:
				return True
	
	elif pitchClassB > pitchClassA:
		for interval in ILLEGAL_INTERVALS:
			if (pitchClassA + interval) % 12 == pitchClassB:
				return True
	
	return False

class SimpleChord:
	""" Represents a very simple chord. """
	
	scale = ['C', 'D-', 'D', 'E-', 'E', 'F', 'G-', 'G', 'A-', 'A', 'B-', 'B']
	
	def __init__(self, name, quarterLength):
		""" Creates a chord with a name of the form X or Xm with its quarter length. 
		
		>>> sc = SimpleChord('C#', 4)
		>>> sc.name
		'C#'
		"""
		self._quarterLength = quarterLength
		if name[-1] == 'm':
			self._root = name[:-1]
			self._major = False
		else:
			self._root = name
			self._major = True
	
	def getSerious(self):
		""" Returns a music21 chord. 
		
		>>> sc = SimpleChord('C', 4)
		>>> sc.getSerious().root()
		C
		>>> sc.getSerious().determineType()
		'Major Triad'
		>>> scm = SimpleChord('Cm', 4)
		>>> scm.getSerious().determineType()
		'Minor Triad'
		>>> sce = SimpleChord('Am', 4)
		>>> sce.getSerious().determineType()
		'Minor Triad'
		"""
		startpos = self.__class__.scale.index(self._root)
		notenames = [self._root]
		notenames.append(self._circularIndex(startpos + 7))
		if self._major:
			notenames.append(self._circularIndex(startpos + 4))
		else:
			notenames.append(self._circularIndex(startpos + 3))
		return music21.chord.Chord(notenames)
	
	def _getName(self):
		""" Returns the name of the chord. """
		if not self._major:
			return self._root + 'm'
		return self._root
	
	name = property(_getName,
	doc = """ Returns the name of the chord.
	
	>>> SimpleChord('Am', 4).name
	'Am'
	""")
	
	def _getQuarterLength(self):
		""" Returns the quarter length of the chord. """
		return self._quarterLength
	
	quarterLength = property(_getQuarterLength,
	doc = """ Returns the quarter length of the chord. """
	)
	
	def _circularIndex(self, index):
		return self.__class__.scale[index % len(self.__class__.scale)]
	
	def __str__(self):
		return '[%s, %f]' % (self.names, self._quarterLength)

class ChordProgression:
	""" Holds a chord progression with chords and their offsets. """
	
	def __init__(self, chordsWithOnsets = []):
		""" Creates an empty chord progression. 
		
		>>> cp = ChordProgression([('G', 0), ('C', 4)])
		"""
		self._onsetList = []
		self._chordOnsets = {}
		
		for chord, onset in chordsWithOnsets:
			self.addChordAt(chord, onset)
	
	def chordAt(self, quarterTime):
		""" Returns the chord at the provided quarter time.
		
		>>> cp = ChordProgression([('G', 0), ('C', 4)])
		>>> cp.chordAt(3).name
		'G'
		>>> cp.chordAt(5).name
		'C'
		"""
		lastChordOnsetIndex = self._binaryFindIndex(quarterTime)
		lastChordOnset = self._onsetList[lastChordOnsetIndex]
		if lastChordOnsetIndex < len(self._onsetList) - 1:
			duration = self._onsetList[lastChordOnsetIndex + 1] - lastChordOnset
		else:
			duration = 4
		return SimpleChord(self._chordOnsets[lastChordOnset], duration)
	
	def addChordAt(self, chord, quarterTime):
		""" Adds the chord at the provided quarter time. 
		
		No care is taken as to whether a chord already exists at this onset.
		Which means to say, that if this is the case, the existing chord is
		simply overwritten.
		
		>>> cp = ChordProgression([('G', 0), ('C', 4)])
		>>> cp.addChordAt('D', 2)
		>>> cp.chordAt(3).name
		'D'
		>>> cp.chordAt(4).name
		'C'
		"""
		self._chordOnsets[quarterTime] = chord
		self._binaryAdd(quarterTime)
	
	def _binaryAdd(self, quarterTime):
		""" Performs a binary search on the onset list and inserts the new onset time. """
		if not quarterTime in self._onsetList:
			pos = self._binaryFindIndex(quarterTime)
			self._onsetList.insert(pos + 1, quarterTime)
	
	def _binaryFind(self, quarterTime, onlyIndex = False):
		""" Return the last onset prior to the provided quarter time. """
		left = 0
		right = len(self._onsetList) - 1
		current = (left + right)/2
		
		while left <= right and not self._onsetList[current] == quarterTime:
			if self._onsetList[current] < quarterTime:
				left = current + 1
			else:
				right = current - 1
			current = (left + right)/2
		
		if onlyIndex or current == -1:
			return current
		
		return self._onsetList[current]
	
	def __iter__(self):
		""" Returns an iterator for a chord progression. 
		
		>>> cp = ChordProgression([('G', 0), ('C', 4)])
		>>> [c.name for c in cp]
		['G', 'C']
		"""
		return iter([self.chordAt(onset) for onset in self._onsetList])
	
	def _binaryFindIndex(self, quarterTime):
		""" Return the index of the last onset prior to the provided quarter time. """
		return self._binaryFind(quarterTime, True)
	
	def __str__(self):
		""" Returns a string representation of the chord progression.
		
		>>> cp = ChordProgression([('G', 0), ('C', 4)])
		>>> str(cp)
		'G   C   '
		"""
		return ''.join([chord.name.ljust(int(chord.quarterLength)) for chord in self])
	
if __name__ == "__main__":
	import doctest
	doctest.testmod()