# --- Add parent dir to paths for doctest compatiable intra-package imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# --- End of parent loading

import copy
import collections

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
		
		# Order matters
		self._analysums = [
			'instruments', 'melody', 'bandSize'
		]
		
		self._melody = collections.defaultdict(frequency.ConditionalFrequencyDistribution)
		self._instruments = frequency.FrequencyDistribution()
		self._bandSize = 0
		
		self._successful = False
	
	def run(self):
		""" Starts the training. """
		logger.status("Parsing and analysing %i XML files." % len(self._sourceFiles))
		
		self._hitDumps()
		
		if len(self._analysums) > 0:
			for i in range(len(self._sourceFiles)):
				xmlScore = self._sourceFiles[i]
				logger.status("Processing %i of %i. (%s)" % (i+1, len(self._sourceFiles), xmlScore))
				self._processScore(xmlScore)
			
			self._writeDumps()
		
		self._successful = True
		return True
	
	def _processScore(self, xmlScore):
		""" From an XML file process a score. """
		inMemory = self._parse(xmlScore)
		
		# YOU ARE HERE!
		for analysum in self._analysums:
			logger.status("Analysing %s." % analysum)
			getattr(self, '_%sAnalysis' % analysum)(inMemory)
	
	def _hitDumps(self):
		""" Try to get all analysums from dumps and cross them from the todo list if found. """
		todo = copy.deepcopy(self._analysums)
		for analysum in self._analysums:
			logger.status("Looking for previously saved %s analysis." % analysum)
			dump = self._loadFromCorpus(analysum)
			if dump:
				setattr(self, '_' + analysum, dump)
				todo.remove(analysum)
				logger.status("Using previously analysed data.")
			else:
				logger.status("Found no previously analysed data.")
		self._analysums = todo
	
	def _writeDumps(self):
		todo = copy.deepcopy(self._analysums)
		for analysum in self._analysums:
			logger.status("Dumping results of %s analysis." % analysum)
			self._dumpToCorpus(analysum, getattr(self, '_' + analysum))
			todo.remove(analysum)
		self._analysums = todo
	
	def _parse(self, xml):
		if self._collectionName == 'pmlp':
			return corpus.parseWork(xml)
		else:
			return music21.corpus.parseWork(xml)
	
	def _bandSizeAnalysis(self, m21score):
		""" Calls melody analysis if this hasn't been done yet. """
		if len(self._instruments) == 0:
			self._bandSize = 0
		self._bandSize = len(self._instruments.getByPercentage(self._instruments.relativeFrequency(self._instruments.top)/2.0))

	def _instrumentsAnalysis(self, m21score):
		""" Adds a scores instruments to the list of instruments. """
		for part in m21score:
			if not isinstance(part.id, int):
				partName = str(part.id)
				logger.status("Instrument %s occurs in score." % partName)
				self._instruments.seen(partName)
	
	def _melodyAnalysis(self, m21score):
		""" Analyses the melody style of a corpus. """
		logger.status("Creating melody ngrams for a score.")
		
		if not m21score[0]:
			return
		
		for part in m21score:
			self._partMelodyAnalysis(part)
	
	def _partMelodyAnalysis(self, m21part):
		""" Analyses one stream of notes. """
		n = 5
		
		if isinstance(m21part.id, int):
			return
		
		partName = str(m21part.id)
		partNotes = m21part.flat.notes
		
		if len(partNotes) < n:
			return
		
		for i in range(0, len(partNotes) - n):
			# THIS IS NECESSARY MAGIC!
			sNT = partNotes[i:i+n]
			[note for note in sNT]
			# EOM
			noteNGram = ngram.NoteNGram(sNT)
			self._melody[partName].seenOnCondition(noteNGram.condition, noteNGram.sample)
		
		logger.status("Conditional frequency distribution for %s has %i conditions." % (partName, len(self._melody[partName])))
	
	def _loadFromCorpus(self, dataType):
		return corpus.persistence.load(dataType, self._collectionName, self._corpusName)
	
	def _dumpToCorpus(self, dataType, data):
		corpus.persistence.dump(dataType, data, self._collectionName, self._corpusName)
	
	def _getResults(self):
		""" Return the results of the training run. """
		if not self._successful:
			raise StateError("no results available yet")
		
		return {
			'melody' : self._melody,
			'bandSize' : self._bandSize,
			'instruments' : self._instruments
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
            
    