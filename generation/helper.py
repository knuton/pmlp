def combineSubparts(part, subparts = [], introOutro = [], numOfRepeats = 1):
	""" Takes a part and a list of subparts and appends the subparts' contents to the part. """
	# using repeatAppend because that creates a copy of the measure which helps keeping the right order
	part.repeatAppend(introOutro, numOfRepeats)
	
	for subpart in subparts:
		for measure in subpart:
			part.repeatAppend(measure, 1)
	
	part.repeatAppend(introOutro, numOfRepeats)

def resetContext(music21Obj):
	""" Resets the context of a music21 object or a list of music21 objects. """
	music21Obj.offset = 0
	music21Obj.measureNumber = 0
	
	return music21Obj

def resetContexts(parts):
	""" Resets the context of objects contained in the parts contained in the list. """
	for part in parts:
		for item in part:
			resetContext(item)