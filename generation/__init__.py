# --- Add parent dir to paths for doctest compatiable intra-package imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# --- End of parent loading

import music21.stream
import music21.note

import random
import difflib

from statistics import ngram
from statistics import frequency
from tools import logger, music42
from common.exceptions import StateError
from music import chordial
from tools import mididicts

class Generator:
	""" Generates a new song from conditional frequency distributions. """
	
	def __init__(self, resultSet):
		""" Fills the generator with the available data. """
		self._structure = 'structure' in resultSet and resultSet['structure'] or None
		self._melody = resultSet['melody']
		self._instruments = resultSet['instruments']
		self._bandSize = resultSet['bandSize']
		
		# Usewinner is either useId or useMidi
		self._useWinner = resultSet['useWinner']
		
		self._midiProgs = resultSet['midiPrograms']
		
		# the instrument choices that were made 
		self._instrChoices = resultSet['instrChoices']
		
		# this ways the program uses midiProgs as instruments if it wants to
		if self._useWinner == "midiUse":
			self._instruments = self._midiProgs
		
		if len(self._instrChoices) > 0:
			self._activeInstruments = self._instrChoices
		else:
			self._activeInstruments = self._instruments.topN(self._bandSize)
		
		self._activeStructure = None
		self._alphabets = {}
		for instrument in self._activeInstruments:
			self._alphabets[instrument] = self._melody[instrument].sampleSpace
		
		self._melodyFree = True
	
	
	def _generatePart(self, partName, measureNum, measureLen):
		""" Generates a part from its available data on call. """
		currOffset = 0.0

		# random starting point
		history = random.choice(self._melody[partName].conditions)
		logger.status("Starting from " + str(history))
		
		
		
		part = music21.stream.Part()
		
		# insert instrument information:
		partInstr = part.getInstrument()
		if self._useWinner == "midiUse": 
			partInstr.midiProgram = int(partName) # This makes the parts sound different!
			partInstr.partName = str(mididicts.midiAlphabet[partInstr.midiProgram])
		elif self._useWinner == "idUse":
			# try to find a suitable midiProgram by comparing the name of the part with 128 different instrument names
			compare = " " + str(partName) + " "
			simInstruments = difflib.get_close_matches(compare, mididicts.midiNameAlphabet.keys())
			
			# if successful: use the corresponding midiProgram
			if len(simInstruments) > 0:
				simInstrument = simInstruments[0]
				partInstr.midiProgram = int(mididicts.midiNameAlphabet[simInstrument])
				partInstr.partName = str(mididicts.midiAlphabet[partInstr.midiProgram])
			else:
				partInstr.partName = str(partName)
			
		# assign random id (produces errors and doesnt seem necessary)
		#partInstr.partIdRandomize()
		
		# generate scoreInstrument information (seems necessary)
		partInstr.instrumentId = partInstr.partId
		partInstr.instrumentName = partInstr.partName
		
		part.insert(0, partInstr)
		
		
		# Insert instrument specific generation procedures here
		# using instrumentGroups might be helpful
		
		
		restMeasure = music21.stream.Measure()
		rest = music21.note.Rest()
		rest.quarterLength = 4
		restMeasure.append(rest)
		
		
		#-----------------------------------------------------------------#
		# Melody
		
		if partInstr.midiProgram in mididicts.instrumentGroups["melody"] and self._melodyFree:
		
			musicSamplesMeasures = [1,2]
			
			# loop to avoid index errors when generating verse and so on
			while len(musicSamplesMeasures) < 14:
				# create some music
				score = []
				for note in history:
					score.append(self._fixNote(note, currOffset))
					currOffset += note.quarterLength
		
				# the limit is quite high to avoid index out of range errors below
				while currOffset < measureNum * 3 * measureLen:
					nextNote = self._predictNote(history, partName)
			
					score.append(self._fixNote(nextNote, currOffset))
					currOffset += nextNote.quarterLength
			
					history = history[1:] + (nextNote,)
					logger.status("Current history is " + str(history))
			
				# create a part
				musicSamples = music21.stream.Part()
				for note in score:
					musicSamples.append(note)
			
				# reset the values
				currOffset = 0.0

				# random starting point
				history = random.choice(self._melody[partName].conditions)
				logger.status("Starting from " + str(history))
			
				# extract measures
				musicSamplesMeasures = musicSamples.makeMeasures()
								
			# create song components from measures
			
			intrOutro = []
			intrOutro.append(musicSamplesMeasures[0])
			intrOutro.append(musicSamplesMeasures[1])
			
			verse = []
			verse.append(musicSamplesMeasures[2])
			verse.append(musicSamplesMeasures[3])
			verse.append(musicSamplesMeasures[4])
			verse.append(musicSamplesMeasures[5])
			
			chorus = []
			chorus.append(musicSamplesMeasures[6])
			chorus.append(musicSamplesMeasures[7])
			chorus.append(musicSamplesMeasures[8])
			chorus.append(musicSamplesMeasures[9])
		
			bridge = []
			bridge.append(musicSamplesMeasures[10])
			bridge.append(musicSamplesMeasures[11])
			bridge.append(musicSamplesMeasures[12])
			bridge.append(musicSamplesMeasures[13])
		
			#delete offset information
			for m in intrOutro:
				m.offset = 0
				m.measureNumber = 0
			for m in verse:
				m.offset = 0
				m.measureNumber = 0 	
			for m in chorus:
				m.offset = 0
				m.measureNumber = 0
			for m in bridge:
				m.offset = 0
				m.measureNumber = 0
			
			# fill the part
			# using repeatAppend because that creates a copy of the measure which helps keeping the right order 
			for m in intrOutro:
				part.repeatAppend(m,1)
			
			for m in verse:
				part.repeatAppend(m,1)
			for m in verse:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
			for m in verse:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
			for m in bridge:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
				
			for m in intrOutro:
				part.repeatAppend(m,1)
				
			self._melodyFree = False
		
		#-----------------------------------------------------------------#
		# Drums
		
		elif partInstr.midiProgram in mididicts.instrumentGroups["rhythm"] or not self._melodyFree:
		#else:
			musicSamplesMeasures = [1,2]
			# loop to avoid index errors when generating verse and so on
			while len(musicSamplesMeasures) < 6:
				# create some music
				score = []
				for note in history:
					score.append(self._fixNote(note, currOffset))
					currOffset += note.quarterLength
		
				# the limit is quite high to avoid index out of range errors below
				while currOffset < measureNum * 3 * measureLen:
					nextNote = self._predictNote(history, partName)
			
					score.append(self._fixNote(nextNote, currOffset))
					currOffset += nextNote.quarterLength
			
					history = history[1:] + (nextNote,)
					logger.status("Current history is " + str(history))
			
				# create a part
				musicSamples = music21.stream.Part()
				for note in score:
					musicSamples.append(note)
				
				# reset the values
				currOffset = 0.0

				# random starting point
				history = random.choice(self._melody[partName].conditions)
				logger.status("Starting from " + str(history))
				
				# extract measures
				musicSamplesMeasures = musicSamples.makeMeasures()
			
			# create song components
			verse = []
			verse.append(musicSamplesMeasures[1])
			verse.append(musicSamplesMeasures[1])
			verse.append(musicSamplesMeasures[1])
			verse.append(musicSamplesMeasures[2])
			
			chorus = []
			chorus.append(musicSamplesMeasures[3])
			chorus.append(musicSamplesMeasures[3])
			chorus.append(musicSamplesMeasures[3])
			chorus.append(musicSamplesMeasures[4])
		
			bridge = []
			bridge.append(musicSamplesMeasures[5])
			bridge.append(musicSamplesMeasures[5])
			bridge.append(musicSamplesMeasures[5])
			bridge.append(musicSamplesMeasures[5])
			
			#delete offset information
			for m in verse:
				m.offset = 0
				m.measureNumber = 0
			for m in chorus:
				m.offset = 0
				m.measureNumber = 0
			for m in bridge:
				m.offset = 0
				m.measureNumber = 0
			
			# fill the part
			part.repeatAppend(restMeasure,2)
			
			for m in verse:
				part.repeatAppend(m,1)
			for m in verse:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
			for m in verse:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
			for m in bridge:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
				
			part.repeatAppend(restMeasure,2)
		
		#-----------------------------------------------------------------#
		# all the rest
		
		else:
			musicSamplesMeasures = [1,2]
			# loop to avoid index errors when generating verse and so on
			while len(musicSamplesMeasures) < 6:
				# create some music
				score = []
				for note in history:
					score.append(self._fixNote(note, currOffset))
					currOffset += note.quarterLength
		
				# the limit is quite high to avoid index out of range errors below
				while currOffset < measureNum * 3 * measureLen:
					nextNote = self._predictNote(history, partName)
			
					score.append(self._fixNote(nextNote, currOffset))
					currOffset += nextNote.quarterLength
			
					history = history[1:] + (nextNote,)
					logger.status("Current history is " + str(history))
			
				# create a part 
				musicSamples = music21.stream.Part()
				for note in score:
					musicSamples.append(note)
				
				# reset the values
				currOffset = 0.0

				# random starting point
				history = random.choice(self._melody[partName].conditions)
				logger.status("Starting from " + str(history))
				
				# extract measures
				musicSamplesMeasures = musicSamples.makeMeasures()
			
			# create song components
			verse = []
			verse.append(musicSamplesMeasures[1])
			verse.append(musicSamplesMeasures[1])
			verse.append(musicSamplesMeasures[1])
			verse.append(musicSamplesMeasures[2])
			
			chorus = []
			chorus.append(musicSamplesMeasures[3])
			chorus.append(musicSamplesMeasures[4])
			chorus.append(musicSamplesMeasures[3])
			chorus.append(musicSamplesMeasures[4])
		
			bridge = []
			bridge.append(musicSamplesMeasures[5])
			bridge.append(musicSamplesMeasures[6])
			bridge.append(musicSamplesMeasures[6])
			bridge.append(musicSamplesMeasures[5])
		
			#delete offset information
			for m in verse:
				m.offset = 0
				m.measureNumber = 0
			for m in chorus:
				m.offset = 0
				m.measureNumber = 0
			for m in bridge:
				m.offset = 0
				m.measureNumber = 0
			
			# fill the part
			
			part.repeatAppend(restMeasure,2)
			
			for m in verse:
				part.repeatAppend(m,1)
			for m in verse:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
			for m in verse:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
			for m in bridge:
				part.repeatAppend(m,1)
			for m in chorus:
				part.repeatAppend(m,1)
			
			part.repeatAppend(restMeasure,2)
		
		"""	
		# old generation procedure
		else: 	
			# use old generation method 
			score = []
			for note in history:
				score.append(self._fixNote(note, currOffset))
				currOffset += note.quarterLength
		
			while currOffset < measureNum * measureLen: 
				nextNote = self._predictNote(history, partName)
			
				score.append(self._fixNote(nextNote, currOffset))
				currOffset += nextNote.quarterLength
			
				history = history[1:] + (nextNote,)
				logger.status("Current history is " + str(history))
		
		
			# put all the music into the part
			for note in score:
			#	print note.quarterLength
				part.append(note)
		"""
	
		return part
	
	def _generateStructure(self, measureNum, measureLen):
		""" Generates a chord structure for the score. """
		currOffset = 0.0
		
		history = random.choice(self._structure[self._instruments.top].conditions)
		logger.status("Starting from " + str(history))
		
		chordProg = chordial.ChordProgression()
		for chord in history:
			chordProg.addChordAt(chord.name, currOffset)
			currOffset += chord.quarterLength
		
		while currOffset < measureNum * measureLen:
			nextChord = self._predictChord(history)
			
			chordProg.addChordAt(nextChord.name, currOffset)
			currOffset += nextChord.quarterLength
			
			history = history[1:] + (nextChord,)
			logger.status("Current history is %s" % str(history))
		
		self._activeStructure = chordProg
	
	def _fixNote(self, note, offset):
		""" Fixes a note. """
		if not self._activeStructure:
			return music42.makeCmaj(note)
		
		while not self._activeStructure.chordAt(offset).isCompatible(note):
			logger.status("Transposing %s." % str(note))
			return note.transpose(-1)
	
	def generate(self):
		""" Generate a whole new score. """
		measureNum = 32
		measureLen = 4
		
		s = music21.stream.Score()
		
		logger.status("Generating structure for score.")
		self._generateStructure(measureNum, measureLen)
		
		
		for instrument in self._activeInstruments:
			logger.status("Generating part for %s." % instrument)
			# TODO determine measureNum and measureLen through analysis
			newPart = self._generatePart(instrument, measureNum, measureLen)
			
			# check and change conflicting notes
			e = 0
			while e < len(newPart) - 1:
			#for elem in range(len(newPart)):
				while not isinstance(newPart[e], music21.stream.Measure):
					e = e + 1
				newM = newPart[e]
				for oldPart in s:
					oldM = oldPart[e]
					for elem in newM:
						sameOffset = []
						# dont use .isNote (isinstance produces less errors because only few objects have an isNote function)
						if isinstance(elem, music21.note.Note): 
							for oelem in oldM: 
								if isinstance(oelem, music21.note.Note):
									# all notes that overlap with the current note are stored in sameOffset
									if elem.offset in range(oelem.offset, (oelem.offset + oelem.quarterLength)) or oelem.offset in range(elem.offset, (elem.offset + elem.quarterLength)):
										sameOffset.append(oelem)
						# if overlapping notes were found:
						if sameOffset:
							for i in range(len(sameOffset)):
								for j in range(len(sameOffset)):
									k = 0
									while self._areConflicting(sameOffset[i], elem) or self._areConflicting(sameOffset[j], elem): 
										logger.status("transposing: %s" % str(elem))
										elem = elem.transpose(-1)
										logger.status("transposed: %s" % str(elem))
										# k prevents infinite loops
										k = k + 1
										if k == 40:
											logger.status("%s is not harmonizable" % str(elem))
											break
				e = e + 1
			
			s.insert(0, newPart)

		#self._smoothEnd(s)

		return s
	
	def _completeMeasure(self, part, currQuarterLength, measureLength = 4):
		""" Fills up one measure worth of rests. """
		rest = music21.note.Rest()
		if currQuarterLength < measureLength:
			rest.quarterLength = measureLength - currQuarterLength
			part.append(rest)
			return part # TODO is this necessary? (used?)
		elif currQuarterLength == measureLength:
			rest.quarterLength = measureLength
			part.append(rest)
			return part
	
	def _predictNote(self, realHistory, partName):
		""" Predicts the next note from a history that is being provided. """
		normalizedHistory = music42.normalizeNotes(realHistory)
		
		if self._melody[partName].expected(normalizedHistory):
			return music42.denormalizeNote(self._melody[partName].expectedFuzz(normalizedHistory), realHistory)
		
		logger.log("Failed to find prediction for history %s" % (normalizedHistory,))
		return random.choice(self._alphabets[partName])
	
	def _predictChord(self, history):
		""" Predicts the next chord from a history. """
		if self._structure[self._instruments.top].expected(history):
			return self._structure[self._instruments.top].expectedFuzz(history)
		
		logger.log("Failed to find prediction for history %s" % str(history))
		return random.choice(self._structure[self._instruments.top].sampleSpace)
	
	def _smoothEnd(self, stream):
		longestPart = None
		maxDur = -1
		for part in stream:
			if part.duration.quarterLength > maxDur:
				longestPart = part
				maxDur = part.duration.quarterLength
		
		if self._activeStructure and longestPart:
			lastChord = self._activeStructure[-1].getSerious()
			longestPart.append(music21.note.Note(lastChord.root().pitchClass))
			lastChord.quarterLength = 4
			longestPart.append(lastChord)
			
	# checks if two notes are conflicting 
	def _areConflicting(self, Note1, Note2):
		# conflictlist contains intervals that would produce a conflict
	
		# every note which is 1/2 step above or below produces conflict
		conflictlist = [1,11,13,23,25,35,37,47,49,59,61,71,73,83,85,95,97]
		
		# helmholzlist follows another theory. 
		#conflictlist = [1,2,10,11,13,14,22,23,25,26,34,35,37,38,46,47,49,50,58,59,61,62,70,71]

		if Note1.isNote and Note2.isNote:
			intval = music21.interval.notesToChromatic(Note1,Note2)
			if intval.undirected in conflictlist: 
				return True
			else: 
				return False
		else: 
			return False