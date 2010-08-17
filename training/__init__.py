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

from tools.mididicts import midiAlphabet

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
		
		# midiUse and idUse determine how the trainer trains
		# (whether it uses midiPrograms or only part-ids for training)
		self._midiUse = False
		self._idUse = False
		
		# choosing the instruments yourself? 
		self._instrChoice = False
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
		
		# if there is only one midiProgram used: use idUse 
		if len(self._midiProgs.samples()) == 1:
			self._midiUse = False
			self._idUse = True
		# if there are more ud midiUse 
		elif len(self._midiProgs.samples()) > 1: 
			self._midiUse = True
			self._idUse = False
		# if I made a programming-mistake use idUse
		else: 
			self._midiUse = False
			self._idUse = True
		
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
			
			# check whether midiPrograms or ids should be used for training
			if analysum == 'midiProgs':
				# if there is only one midiProgram used: use idUse 
				if len(self._midiProgs.samples()) == 1:
					self._midiUse = False
					self._idUse = True
				# if there are more ud midiUse 
				elif len(self._midiProgs.samples()) > 1: 
					self._midiUse = True
					self._idUse = False
				# if I made a programming-mistake use idUse
				else: 
					self._midiUse = False
					self._idUse = True
			
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
		if self._idUse: 
			partPrograms = self._instruments.samples()
			partAlphabet = []
			choiceProgs = []
			i = 1
			for id in partPrograms: 
				if id != None: 
					partAlphabet.append((i, str(id)))
					choiceProgs.append(str(i))
					i = i + 1
			choiceAlphabet = dict(partAlphabet)
			print "choiceAlphabet"
			print choiceAlphabet
			
		elif self._midiUse:
			choiceAlphabet = midiAlphabet
			choiceProgs = []
			for elem in self._midiProgs.samples(): 
				if int(elem): 
					if len(self._melody[elem].conditions) > 0: 
						choiceProgs.append(str(elem))		
		
		print "\n You can choose between the following instruments: \n"
		for elem in sorted(choiceProgs): 
			if int(elem) in range(1, len(choiceAlphabet)): 
				print " " + str(int(elem)) + "\t" + str(choiceAlphabet[int(elem)]) 
		
		print "\n Enter the corresponding number to choose an instrument you want to use \n"
		print " Enter 'n' when you are finished choosing instruments. "
		print " Enter 'x' if you do not want to make a choice. \n"
		
		iChoice = raw_input(" make your choice: ")
		if iChoice == "x" or iChoice == "n": 
			self._instrChoice = False
		else: 
			self._instrChoice = True
		
		if self._instrChoice:
			while iChoice not in choiceProgs:
				iChoice = raw_input(" Please make a valid choice: ")
				
		if self._instrChoice: 
			while iChoice != "n": 
				if self._idUse:
					self._instrChoices.append(choiceAlphabet[int(iChoice)])
				elif self._midiUse:
					self._instrChoices.append(iChoice)
				iChoice = raw_input(" Anything else?: ")
				if iChoice == "n":
					break
				while iChoice not in choiceProgs:
					iChoice = raw_input(" Please make a valid choice: ")
					if iChoice == "n": 
						break
			
			print "\n The following instruments will be used: \n"
			
			if self._idUse: 
				for elem in self._instrChoices: 
					print "\t" + str(elem)
			
			elif self._midiUse:
				for elem in self._instrChoices: 
					print "\t"+str(choiceAlphabet[int(elem)]) 
			print
	
		elif not self._instrChoice: 
			print " Ok then I will choose the instruments"
		
	def _bandSizeAnalysis(self, m21score):
		""" Calls melody analysis if this hasn't been done yet. """
		if len(self._instruments) == 0:
			self._bandSize = 0
		
		# if idUse is used: calculate using instruments
		if self._idUse: 
			self._bandSize = len(self._instruments.getByPercentage(self._instruments.relativeFrequency(self._instruments.top)/2.0))
		# if midiUse is used: calculate using midiProgs
		if self._midiUse: 
			self._bandsize = len(self._midiProgs.getByPercentage(self._instruments.relativeFrequency(self._instruments.top)/2.0))	
		
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
		
		# What is this good for?
		#if isinstance(m21part.id, int):
		#	return
		
		# if useID train on ids
		if self._idUse: 
			partName = str(m21part.id)
		
		# else train on midiPrograms 
		elif self._midiUse: 
			partInstr = m21part.getInstrument()
			partName = str(partInstr.midiProgram)
					
		else: 
			return
		
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
		
		#if isinstance(m21part.id, int):
		#	return
		
		# if useID train on ids
		if self._idUse: 
			partName = str(m21part.id)
		
		elif self._midiUse: 
			partInstr = m21part.getInstrument()
			partName = str(partInstr.midiProgram)
		
		else: 
			return
		
		chordProg = chordial.fromNotes(m21part)
		
		for i in range(0, len(chordProg) - n):
			chordNGram = ngram.ChordNGram(chordProg[i:i+n])
			self._structure[partName].seenOnCondition(chordNGram.condition, chordNGram.sample)
		
		logger.status("Conditional frequency distribution for %s has %i conditions." % (partName, len(self._structure[partName])))
	
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
		elif self._idUse: 
			useWinner = "idUse"
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
            
    