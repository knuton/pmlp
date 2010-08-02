import music21
import logger

cMajScale = [0,2,4,5,7,9]
cMinScale = [0,2,3,5,7,8,10]
cFour = music21.note.Note()

def normalizeNotes(noteSequence = []):
	""" Normalizes a sequence of notes to one with same intervals, but starting on C4.
	
	>>> import music21
	>>> s = music21.stream.Stream()
	>>> s.append(music21.note.Note('D'))
	>>> s.append(music21.note.Note('G', type = 4))
	>>> s.duration.quarterLength
	5.0
	>>> normalized = normalizeNotes(s)
	>>> s2 = music21.stream.Stream()
	>>> for note in normalized:
	...   s2.append(note)
	>>> s2.duration.quarterLength
	5.0
	"""
	# We need to use an actual note with pitch to determine the distance to C4,
	# not a rest or other note-like object.
	firstNote = firstActualNote(noteSequence)
	# notesToInterval uses C4 by default
	if firstNote:
		distanceToC = music21.interval.notesToInterval(firstNote)
		noteSequence = music21.stream.Stream(noteSequence).transpose(distanceToC)
	return tuple([makeNote(note) for note in noteSequence])

def firstActualNote(noteSequence):
	""" Returns the first actual note in the sequence or None, if none is found. """
	firstNote = next((note for note in noteSequence if note.isNote), None)
	return firstNote and makeNote(firstNote) or None

def denormalizeNote(note, unnormalHistory):
	""" De-normalizes a note generated form a normalized history using its unnormalized history. """
	if note.isNote:
		by = firstActualNote(unnormalHistory)
		logger.debug(str(by) + ' applied to ' + str(note)) # DEBUG
		return by and makeNote(note.transpose(music21.interval.notesToInterval(cFour, by))) or note
	else:
		return note

def makeCmaj(note):
	""" Takes a note and 'corrects' it to C major scale. """
	if not note.isNote:
		return note
	while note.pitchClass not in cMajScale:
		note = note.transpose(-1)
	return note

def makeNote(noteObj):
	""" Makes a standardized note from some note object.
	
	Notes
	>>> g4 = music21.note.Note('G', type = 4)
	>>> g4Copy = makeNote(g4)
	>>> g4.duration.quarterLength
	4.0
	
	Chords
	>>> gmaj4 = makeNote(music21.chord.Chord(['G', 'B', 'D'], type = 4))
	>>> gmaj4.duration.quarterLength
	4.0
	"""
	if noteObj.isNote:
		note = music21.note.Note(type = noteObj.duration.quarterLength)
		note.pitch.midi = noteObj.pitch.midi
		return note
	elif noteObj.isRest:
		rest = music21.note.Rest()
		rest.duration = music21.duration.Duration(noteObj.duration.quarterLength)
		return rest
	elif noteObj.isChord:
		return music21.chord.Chord(noteObj.pitchClasses, type = noteObj.duration.quarterLength)
	else:
		return music21.note.Note()

if __name__ == "__main__":
	import doctest
	doctest.testmod()