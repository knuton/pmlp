import nltk.probability

import music21.corpus
import music21.stream

from statistics import ngram

# Load XML
bachXMLCorpus = music21.corpus.getComposer('bach', 'xml')[0:49]

# Parse XML
bachCorpus = [music21.corpus.parseWork(xmlScore) for xmlScore in bachXMLCorpus]

# Get flattened Soprano parts (ignore scores without Soprano)
flattenedSopranos = [score.getElementById('Soprano').flat for score in bachCorpus if score.getElementById('Soprano')]

trigrams = []

for soprano in flattenedSopranos[0:1]: #remove
	if len(soprano.notes) < 3:
		continue
	prevprev = soprano.notes[-2]
	prev = soprano.notes[-1]	
	for note in soprano.notes:
		print note
		trigrams.append(ngram.NoteNGram(music21.stream.Stream([prevprev, prev, note])))
		prevprev = prev
		prev = note

print trigrams
