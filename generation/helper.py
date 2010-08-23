def combineSubparts(part, subparts = [], introOutro = [], numOfRepeats = 1):
	""" Takes a part and a list of subparts and appends the subparts' contents to the part. """
	# using repeatAppend because that creates a copy of the measure which helps keeping the right order
	part.repeatAppend(introOutro, numOfRepeats)
	
	for subpart in subparts:
		for measure in subpart:
			part.repeatAppend(measure, 1)
	
	part.repeatAppend(introOutro, numOfRepeats)