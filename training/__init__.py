# --- Add parent dir to paths for doctest compatiable intra-package imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# --- End of parent loading

import music21.corpus
import music21.stream

import corpus.persistence
from statistics import ngram
from statistics import frequency
from tools import logger, music42
from common.exceptions import StateError

class Trainer:
	""" Oversees the training on a collection of MusicXML files. """
	
	def __init__(self, corpusCollection, corpusName, xmls = []):
		""" Creates the trainer. """
		if not corpusCollection in ['music21', 'pmlp']:
			raise ValueError('Unknown corpus collection.')
		self._collectionName = corpusCollection
		self._corpusName = corpusName
		self._sourceFiles = xmls
		self._parsedCorpus = []
		self._successful = False
	
	def run(self):
		""" Starts the training. """
		logger.status("Parsing XML files.")
		self._parsedCorpus = [self._parse(xmlScore) for xmlScore in self._sourceFiles]
		
		logger.status("Analysing melody.")
		self._analyseMelody()
		
		logger.status("Analysing more stuff later. :)")
		
		self._successful = True
		return True
	
	def _parse(self, xml):
		if self._collectionName == 'pmlp':
			return corpus.parseWork(xml)
		else:
			return music21.corpus.parseWork(xml)
	
	def _analyseMelody(self):
		""" Analyses the melody style of a corpus. """
		melodyCFD = self._loadFromCorpus('melody')
		
		if not melodyCFD:
			logger.status("Found no previously analysed data.")
			# Get flattened parts
			flattenedParts = [score[0].flat for score in self._parsedCorpus if score[0]]
			
			trigrams = []
			n = 5
			
			for score in flattenedParts: #remove
				scoreNotes = score.notes
				if len(scoreNotes) < n:
					continue
				for i in range(0, len(scoreNotes) - n):
					logger.status("Creating melody ngrams for a score.")
					# THIS IS NECESSARY MAGIC!
					sNT = scoreNotes[i:i+n]
					[note for note in sNT]
					# EOM
					trigrams.append(ngram.NoteNGram(sNT))
			
			melodyCFD = frequency.ConditionalFrequencyDistribution([noteNGram.conditionTuple for noteNGram in trigrams])
			self._dumpToCorpus('melody', melodyCFD)
		else:
			logger.status("Using previously analysed data.")
		
		self._melody = melodyCFD
	
	def _loadFromCorpus(self, dataType):
		return corpus.persistence.load(dataType, self._collectionName, self._corpusName)
	
	def _dumpToCorpus(self, dataType, data):
		corpus.persistence.dump(dataType, data, self._collectionName, self._corpusName)
	
	def _getResults(self):
		""" Return the results of the training run. """
		if not self._successful:
			raise StateError("no results available yet")
		
		return {
			'melody' : self._melody
		}
	
	results = property(_getResults,
	doc = """ Return the results obtained by training or loaded from dump.
	
	Throws StateError if no results have been computed yet.
	
	>>> coach = Trainer()
	>>> coach.results
	Traceback (most recent call last):
		...
	StateError: no results available yet
	>>> coach.run()
	True
	>>> coach.results
	""")

if __name__ == '__main__':
	import doctest
	doctest.testmod()
            
    