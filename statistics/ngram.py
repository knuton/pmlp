class NGram:
	""" An n-gram is a sequence of n items, taken from a larger sequence.

	This is a general superclass for specific n-gram classes, unigrams, bigrams, trigrams, etc. 
	"""

	def __init__(self, iterableSequence):
		""" Create an n-gram.

		Accepts as input an iterable object of length n and will create an n-gram.

		>>> NGram([]).n
		0
		>>> unibitrigram = NGram([1,2,3])
		>>> unibitrigram.sequence.__class__
		<type 'tuple'>
		>>> unibitrigram.n == len(unibitrigram.sequence)
		True
		>>> unibitrigram.sequence
		(1, 2, 3)
		"""
		self._sequence = tuple(iterableSequence)
		self._n = len(self.sequence)
	
	def _getN(self):
		""" Return the n for this n-gram, meaning its number of items. """
		return self._n
	
	n = property(_getN)

	def _getSequence(self):
		""" Return the items as a tuple. """
		return self._sequence
	
	sequence = property(_getSequence)

class NoteNGram(NGram):
	""" An n-gram for normalized (startnote is C4) melody fragments, incorporating pitch and duration of n notes.

	>>> from music21 import note
	>>> d = note.Note('D5')
	>>> d.quarterLength = 4
	>>> f = note.Note('F6')
	>>> f.quarterLength = 3
	>>> csharp = note.Note('C#3')
	>>> csharp.quarterLength = 1.5
	>>> from music21 import stream
	>>> melodyFragment = stream.Stream()
	>>> melodyFragment.append([d, f, csharp])
	>>> [noteItem.nameWithOctave for noteItem in melodyFragment.notes]
	['D5', 'F6', 'C#3']
	>>> noteTrigram = NoteNGram(melodyFragment)
	>>> [noteItem.nameWithOctave for noteItem in noteTrigram.sequence]
	['C4', 'E-5', 'B1']
	"""

	def __init__(self, noteSequence):
		""" Create a note n-gram.

		Accepts a stream (music21.stream) of note objects and saves their normalized interval sequence.

		>>> NoteNGram([])
		Traceback (most recent call last):
			...
		ValueError: argument has to be a note21.stream.Stream object
		"""

		import music21.note
		import music21.interval
		import music21.stream

		if not isinstance(noteSequence, music21.stream.Stream):
			raise ValueError("argument has to be a note21.stream.Stream object")
		
		# notesToInterval uses C4 by default
		distanceToC = music21.interval.notesToInterval(noteSequence.notes[0])
		
		NGram.__init__(self, noteSequence.transpose(distanceToC))


if __name__ == "__main__":
	import doctest
	doctest.testmod()
