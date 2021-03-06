# --- Add parent dir to paths for doctest compatiable intra-package imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# --- End of parent loading
import music21.note
import music21.duration
import music21.interval
import music21.stream

import tools.music42
from music import chordial

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
	
	def _getCondition(self):
		""" Returns the sequence of conditions, i.e. all but the last item. """
		return self.sequence[:-1]
	
	condition = property(_getCondition,
	doc = """ Returns the sequence of conditions, i.e. all but the last item. 
	
	>>> NGram(['a', 'b', 'c']).condition
	('a', 'b')
	>>> NGram([]).condition
	()
	""")
	
	def _getSample(self):
		""" Returns the sample, i.e. the last item. """
		if len(self.sequence) == 0:
			return None
		return self.sequence[-1]
	
	sample = property(_getSample,
	doc = """ Returns the sample, i.e. the last item.
	
	>>> NGram(['a', 'b', 'c']).sample
	'c'
	>>> NGram([]).sample
	""")
	
	def _getConditionTuple(self):
		""" Return a pair with first projection sequence[0:n-1], second projection sequence[n-1].
		
		So the first projection is a tuple of n-1 elements, the second is a single element.
		
		>>> NGram(['a', 'b', 'c'])._getConditionTuple()
		(('a', 'b'), 'c')
		"""
		return (self.condition, self.sample)
	
	conditionTuple = property(_getConditionTuple)
	
	def __str__(self):
		return '(%s)' % ', '.join([str(item) for item in self.sequence])

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
	['C4', 'D#5', 'B1']
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
		
		noteSequence = tools.music42.normalizeNotes(noteSequence)
		
		NGram.__init__(self, noteSequence)

class ChordNGram(NGram):
	""" An ngram for chords, incorporating chords and their quarter length. """
	
	def __init__(self, chordSequence = []):
		""" Create an ngram from a chord sequence. 
		
		>>> ChordNGram(['G', 'C'])
		Traceback (most recent call last):
			...
		ValueError: Chord sequence needs to consist of SimpleChord objects
		>>> str(ChordNGram([chordial.SimpleChord('G', 8), chordial.SimpleChord('Am', 4), chordial.SimpleChord('C', 4)]))
		'(G, Am, C)'
		
		"""
		for chord in chordSequence:
			if not isinstance(chord, chordial.SimpleChord):
				raise ValueError("Chord sequence needs to consist of SimpleChord objects")
				
		NGram.__init__(self, chordSequence)


if __name__ == "__main__":
	import doctest
	doctest.testmod()
