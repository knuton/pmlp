import music21
import logger

def normalizeNotes(noteSequence = []):
	# We need to use an actual note with pitch to determine the distance to C4,
	# not a rest or other note-like object.
	firstNote = next((note for note in noteSequence if note.isNote), None)
	# notesToInterval uses C4 by default
	if firstNote:
		distanceToC = music21.interval.notesToInterval(firstNote)
		noteSequence = music21.stream.Stream(noteSequence).transpose(distanceToC)
	return tuple([makeNote(note) for note in noteSequence])
	
def makeNote(noteObj):
	if noteObj.isNote:
		return music21.note.Note(str(noteObj.pitch), type = noteObj.duration.quarterLength)
	elif noteObj.isRest:
		rest = music21.note.Rest()
		rest.duration = music21.duration.Duration(noteObj.duration.quarterLength)
		return rest
	elif noteObj.isChord:
		return music21.chord.Chord(noteObj.pitchClasses, type = noteObj.duration.quarterLength)
	else:
		return music21.note.Note()