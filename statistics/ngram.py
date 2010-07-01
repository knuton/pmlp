import music21.note
import music21.duration
import music21.interval
import music21.stream

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
	
	def _getConditionTuple(self):
		""" Return a pair with first projection sequence[0:n-1], second projection sequence[n-1].
		
		So the first projection is a tuple of n-1 elements, the second is a single element.
		
		>>> NGram(['a', 'b', 'c'])._getConditionTuple()
		(('a', 'b'), 'c')
		"""
		return (self.sequence[0:self.n-1], self.sequence[self.n-1])
	
	conditionTuple = property(_getConditionTuple)

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
	>>> melodyFragment = stream.Stream()
	>>> melodyFragment.append([note.Rest('half'), f, csharp])
	>>> trigramWithRest = NoteNGram(melodyFragment)
	>>> [noteItem.__class__ for noteItem in trigramWithRest.sequence]
	[<class 'music21.note.Rest'>, <class 'music21.note.Note'>, <class 'music21.note.Note'>]
	>>> [noteItem.nameWithOctave for noteItem in trigramWithRest.sequence if noteItem.isNote]
	['C4', 'G#0']
"""

	def __init__(self, noteSequence):
		""" Create a note n-gram.

		Accepts a stream (music21.stream) of note objects and saves their normalized interval sequence.

		>>> NoteNGram([])
		Traceback (most recent call last):
			...
		ValueError: argument has to be a note21.stream.Stream object
		"""
		if not isinstance(noteSequence, music21.stream.Stream):
			raise ValueError("argument has to be a note21.stream.Stream object")
		
		# We need to use an actual note with pitch to determine the distance to C4,
		# not a rest or other note-like object.
		firstNote = next((note for note in noteSequence if note.isNote), None)
		# notesToInterval uses C4 by default
		if firstNote:
			distanceToC = music21.interval.notesToInterval(firstNote)
			noteSequence = noteSequence.transpose(distanceToC)
		
		NGram.__init__(self, [self.makeNote(item) for item in noteSequence])
	
	def makeNote(self, noteObj):
		if noteObj.isNote:
			return music21.note.Note(str(noteObj.pitch), type = noteObj.duration.quarterLength)
		elif noteObj.isRest:
			rest = music21.note.Rest()
			rest.duration = music21.duration.Duration(noteObj.duration.quarterLength)


if __name__ == "__main__":
	import doctest
	doctest.testmod()
