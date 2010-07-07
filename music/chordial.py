import music21.chord

class SimpleChord:
	""" Represents a very simple chord. """
	
	scale = ['C', 'D-', 'D', 'E-', 'E', 'F', 'G-', 'G', 'A-', 'A', 'B-', 'B']
	
	def __init__(self, name, quarterLength):
		""" Creates a chord with a name of the form X or Xm with its quarter length. """
		self._root = name[0]
		self._quarterLength = quarterLength
		if len(name) > 1:
			self._major = False
		else:
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
	
	def _circularIndex(self, index):
		return self.__class__.scale[index % len(self.__class__.scale)]

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
		>>> cp.chordAt(3)
		'G'
		>>> cp.chordAt(5)
		'C'
		"""
		lastChordOnset = self._binaryFind(quarterTime)
		return self._chordOnsets[lastChordOnset]
	
	def addChordAt(self, chord, quarterTime):
		""" Adds the chord at the provided quarter time. 
		
		No care is taken as to whether a chord already exists at this onset.
		Which means to say, that if this is the case, the existing chord is
		simply overwritten.
		
		>>> cp = ChordProgression([('G', 0), ('C', 4)])
		>>> cp.addChordAt('D', 2)
		>>> cp.chordAt(3)
		'D'
		>>> cp.chordAt(4)
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
	
	def _binaryFindIndex(self, quarterTime):
		""" Return the index of the last onset prior to the provided quarter time. """
		return self._binaryFind(quarterTime, True)
		
if __name__ == "__main__":
	import doctest
	doctest.testmod()