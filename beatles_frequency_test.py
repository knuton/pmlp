import music21.stream

import corpus
import corpus.persistence
from statistics import ngram

# Look for dump of trigrams to save time
trigrams = corpus.persistence.load('melody', 'beatles')

# Compute if no dump was found
if not trigrams:
	# Load XML
	xmlCorpus = corpus.getCollection('beatles')
	
	# Parse XML
	beatlesCorpus = [corpus.parseWork(xmlScore) for xmlScore in xmlCorpus]
	
	# Get flattened Soprano parts (ignore scores without Soprano)
	flattenedSopranos = [score.flat for score in beatlesCorpus]

	trigrams = []
	n = 3

	for soprano in flattenedSopranos: #remove
		sopranoNotes = soprano.notes
		if len(sopranoNotes) < n:
			continue
		for i in range(0, len(sopranoNotes) - n):
			# THIS IS NECESSARY MAGIC!
			sNT = sopranoNotes[i:i+n]
			[note for note in sNT]
			# EOM
			trigrams.append(ngram.NoteNGram(sNT))
	corpus.persistence.dump('melody', 'beatles', trigrams)

freakyDistri = nltk.probability.ConditionalFreqDist([noteNGram.conditionTuple for noteNGram in trigrams])

print freakyDistri
print freakyDistri.N()
for i in range(0, 10):
	print freakyDistri[i].samples(), freakyDistri[i].max()
