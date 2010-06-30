import nltk.probability
from nltk.probability import *

import music21.corpus
import music21.stream

import corpus.persistence
from statistics import ngram

# Look for dump of trigrams to save time
trigrams = corpus.persistence.load('melody', 'bach')

# Compute if no dump was found
if not trigrams:
	# Load XML
	bachXMLCorpus = music21.corpus.getComposer('bach', 'xml')[0:49]

	# Parse XML
	bachCorpus = [music21.corpus.parseWork(xmlScore) for xmlScore in bachXMLCorpus]

	# Get flattened Soprano parts (ignore scores without Soprano)
	flattenedSopranos = [score.getElementById('Soprano').flat for score in bachCorpus if score.getElementById('Soprano')]

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
			noteNGram = ngram.NoteNGram(sNT)
			trigrams.append((noteNGram.sequence[0:n-1], noteNGram.sequence[n-1]))
	# Skip for now
	# corpus.persistence.dump('melody', 'bach', trigrams)

freakyDistri = nltk.probability.ConditionalFreqDist(trigrams)

#MLE:
ngram_model = ConditionalProbDist(freakyDistri, MLEProbDist)


print freakyDistri
print ngram_model
