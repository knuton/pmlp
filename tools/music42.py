import music21
import logger

cFour = music21.note.Note()

def normalizeNotes(noteSequence = []):
	# We need to use an actual note with pitch to determine the distance to C4,
	# not a rest or other note-like object.
	firstNote = firstActualNote(noteSequence)
	# notesToInterval uses C4 by default
	if firstNote:
		distanceToC = music21.interval.notesToInterval(firstNote)
		noteSequence = music21.stream.Stream(noteSequence).transpose(distanceToC)
	return tuple([makeNote(note) for note in noteSequence])

def firstActualNote(noteSequence):
	return next((note for note in noteSequence if note.isNote), None)

def denormalizeNote(note, unnormalHistory):
	""" De-normalizes a note generated form a normalized history using its unnormalized history. """
	if note.isNote:
		by = firstActualNote(unnormalHistory)
		logger.debug(str(by) + ' applied to ' + str(note)) # DEBUG
		return by and note.transpose(music21.interval.notesToInterval(cFour, by)) or note
	else:
		return note

def makeNote(noteObj):
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