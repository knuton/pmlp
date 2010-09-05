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
from music import chordial

from tools import mididicts

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
			'instruments', 'midiProgs', 'melody', 'structure', 'bandSize'
		]
		
		self._structure = collections.defaultdict(frequency.ConditionalFrequencyDistribution)
		self._melody = collections.defaultdict(frequency.ConditionalFrequencyDistribution)
		self._instruments = frequency.FrequencyDistribution()
		self._midiProgs = frequency.FrequencyDistribution()
		self._bandSize = 0
		
		self._successful = False
		
		# midiUse determines how the trainer trains
		# (whether it uses midiPrograms or only part-ids for training)
		self._midiUse = False
		
		# to be filled with instrument choices
		self._instrChoices = []
		
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
		
		self._setMidiUseFlag()
		
		# start instrumentChoice
		self._instrumentChoice()
			
		self._successful = True
		return True
	
	def _processScore(self, xmlScore):
		""" From an XML file process a score. """
		inMemory = self._parse(xmlScore)
		
		# YOU ARE HERE!
		for analysum in self._analysums:
			logger.status("Analysing %s." % analysum)
			getattr(self, '_%sAnalysis' % analysum)(inMemory)
			
			if analysum == 'midiProgs':
				self._setMidiUseFlag()
	
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
		
	def _instrumentChoice(self): 
		""" Ask user which instruments he/she wants to have in the new song """
		availableInstruments = {}
		
		if self._midiUse:
			for prog in self._midiProgs.samples():
				if mididicts.isMidiProgram(prog) and len(self._melody[prog]) > 0:
					availableInstruments[prog] = mididicts.midiAlphabet[int(prog)]
		else:
			i = 1
			for id in self._instruments.samples():
				if id:
					availableInstruments[str(i)] = str(id)
					i = i + 1
			print "availableInstruments"
			print availableInstruments
		
		print "\n You can choose between the following instruments: \n"
		for instrumentNum in sorted(availableInstruments): 
			print " " + str(instrumentNum) + "\t" + str(availableInstruments[instrumentNum]) 
		
		print "\n Enter the corresponding number to choose an instrument you want to use \n"
		print " Enter 'n' when you are finished choosing instruments. "
		print " Enter 'x' if you do not want to make a choice. \n"
		#import pdb 
		#pdb.set_trace()
		while True:
			iChoice = raw_input(" Make your choice: ")
			
			if (len(self._instrChoices) == 0 and iChoice == "x") or iChoice == "n":
				break
			
			if iChoice in availableInstruments:
				if self._midiUse:
					self._instrChoices.append(iChoice)
				else:
					self._instrChoices.append(availableInstruments[iChoice])
			else:
				print " Please make a valid choice."
				continue
			
			print " A number to choose another, 'n' to finish."
		
		if self._instrChoices:
			print "\n The following instruments will be used: \n"
				
			if self._midiUse: 
				for elem in self._instrChoices: 
					print "\t" + str(mididicts.midiAlphabet[int(elem)]) + "\n"
			else:
				for elem in self._instrChoices: 
					print "\t" + str(elem) + "\n"
		else: 
			print " Ok then I will choose the instruments"
		
	def _bandSizeAnalysis(self, m21score):
		""" Calls melody analysis if this hasn't been done yet. """
		if len(self._instruments) == 0:
			self._bandSize = 0
		
		# if midiUse is used: calculate using midiProgs
		if self._midiUse: 
			self._bandSize = len(self._midiProgs.getByPercentage(self._midiProgs.relativeFrequency(self._midiProgs.top)/2.0))
		# if idUse is used: calculate using instruments
		else: 
			self._bandSize = len(self._instruments.getByPercentage(self._instruments.relativeFrequency(self._instruments.top)/2.0))
		
	def _instrumentsAnalysis(self, m21score):
		""" Adds a scores instruments to the list of instruments. """
		for part in m21score:
			# check if its a part
			if isinstance(part, music21.stream.Part): 
				if not isinstance(part.id, int):
					partName = str(part.id)
					logger.status("Instrument %s occurs in score." % partName)
					self._instruments.seen(partName)
	
	def _midiProgsAnalysis(self, m21score): 
		""" Adds a scores midi-programs to the list of midi-programs """
		for part in m21score: 
			if isinstance(part, music21.stream.Part):
				# check if its an instrument 
				partInstr = part.getInstrument()
						
				#if isinstance(part[0], music21.instrument.Instrument): 
				midiProg = partInstr.midiProgram
				logger.status("midi program %s occurs in score." % midiProg)
				self._midiProgs.seen(str(midiProg))
	
	def _melodyAnalysis(self, m21score):
		""" Analyses the melody style of a corpus. """
		logger.status("Creating melody ngrams for a score.")
		
		# What is the next line good for?
		if not m21score[0]:
			return
		
		for part in m21score:
			if isinstance(part, music21.stream.Part):
				self._partMelodyAnalysis(part)
	
	def _partMelodyAnalysis(self, m21part):
		""" Analyses one stream of notes. """
		n = 5
		
		# What is this good for? Sometimes the id was an integer, then it is useless and will likely cause trouble.
		# If this causes/caused trouble tell me (johannes).
		if isinstance(m21part.id, int):
			return
		
		# train on midiPrograms or partIDs
		if self._midiUse: 
			partInstr = m21part.getInstrument()
			partName = str(partInstr.midiProgram)
		else:
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
	
	def _structureAnalysis(self, m21score):
		""" Analyses the chord structure of a score. """
		logger.status("Creating structure ngrams for a score.")
		
		if not m21score[0]:
			return
		
		for part in m21score:
			if isinstance(part, music21.stream.Part):
				self._partStructureAnalysis(part)
	
	def _partStructureAnalysis(self, m21part):
		""" Analyses the chord structure for one stream of notes. """
		n = 3
		
		if isinstance(m21part.id, int):
			return
		
		if self._midiUse: 
			partInstr = m21part.getInstrument()
			partName = str(partInstr.midiProgram)
		else:
			partName = str(m21part.id)
		
		chordProg = chordial.fromNotes(m21part)
		
		for i in range(0, len(chordProg) - n):
			chordNGram = ngram.ChordNGram(chordProg[i:i+n])
			self._structure[partName].seenOnCondition(chordNGram.condition, chordNGram.sample)
		
		logger.status("Conditional frequency distribution for %s has %i conditions." % (partName, len(self._structure[partName])))
	
	def _setMidiUseFlag(self):
		""" Look at existing data and set flag for use of partId or midi based instrumentation. """
		# MIDI gets used if there is more than one MIDI program in the data
		self._midiUse = len(self._midiProgs) > 1
	
	def _loadFromCorpus(self, dataType):
		return corpus.persistence.load(dataType, self._collectionName, self._corpusName)
	
	def _dumpToCorpus(self, dataType, data):
		corpus.persistence.dump(dataType, data, self._collectionName, self._corpusName)
	
	def _getResults(self):
		""" Return the results of the training run. """
		if not self._successful:
			raise StateError("no results available yet")
		
		if self._midiUse: 
			useWinner = "midiUse"
		else: 
			useWinner = "idUse"
		
		return {
			'melody' : self._melody,
			'bandSize' : self._bandSize,
			'instruments' : self._instruments,
			'midiPrograms' : self._midiProgs, 
			'structure' : self._structure, 
			'useWinner' : useWinner, 
			'instrChoices' : self._instrChoices 
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
            
    