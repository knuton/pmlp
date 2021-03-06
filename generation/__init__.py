# --- Add parent dir to paths for doctest compatiable intra-package imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# --- End of parent loading

import music21

import random
import difflib

from statistics import ngram
from statistics import frequency
from tools import logger, music42
from common.exceptions import StateError
from music import chordial
from tools import mididicts
import helper

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
	
	def _insertInstrument(self, part, partName):
		""" Generates an instrument for a Part object fitting the provided partName. """
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
		
		# generate scoreInstrument information
		partInstr.instrumentId = partInstr.partId
		partInstr.instrumentName = partInstr.partName
		
		part.insert(0, partInstr)
		
		return partInstr
	
	def _generatePart(self, partName, measureNum, measureLen):
		""" Generates a part from its available data on call. """
		currOffset = 0.0
		# random starting point
		history = random.choice(self._melody[partName].conditions)
		logger.status("Starting from " + str(history))
		
		part = music21.stream.Part()
		
		partInstr = self._insertInstrument(part, partName)
		
		
		# Insert instrument specific generation procedures here
		# using instrumentGroups might be helpful
		
		
		restMeasure = music21.stream.Measure()
		rest = music21.note.Rest()
		rest.quarterLength = 4
		restMeasure.append(rest)
		
		#-----------------------------------------------------------------#
		# Define inner functions for reuse, but which need access to local variables.
		
		def _createMeasuresWithLength(length, musicSamplesMeasures = [1,2]):
			localHistory = history
			localCurrOffset = currOffset
			# loop to avoid index errors when generating verse and so on
			while len(musicSamplesMeasures) < length:
				# create some music
				score = []
				for note in localHistory:
					score.append(self._fixNote(note, localCurrOffset))
					localCurrOffset += note.quarterLength
				
				# the limit is quite high to avoid index out of range errors below
				while localCurrOffset < measureNum * 4 * measureLen:
					nextNote = self._predictNote(localHistory, partName)
					
					score.append(self._fixNote(nextNote, localCurrOffset))
					localCurrOffset += nextNote.quarterLength
					
					localHistory = localHistory[1:] + (nextNote,)
					logger.status("Current history is " + str(localHistory))

				# create a part
				musicSamples = music21.stream.Part()
				for note in score:
					musicSamples.append(note)

				# reset the values
				localCurrOffset = 0.0

				# new random starting point
				localHistory = random.choice(self._melody[partName].conditions)

				# extract measures
				musicSamplesMeasures = musicSamples.makeMeasures()

			return musicSamplesMeasures
		
		#-----------------------------------------------------------------#
		# Melody
		
		if partInstr.midiProgram in mididicts.instrumentGroups["melody"] and self._melodyFree:
		
			musicSamplesMeasures = _createMeasuresWithLength(14)
			
			# create song components from measures
			intrOutro = []
			intrOutro.append(musicSamplesMeasures[0])
			intrOutro.append(musicSamplesMeasures[1])
			
			freemel = True
			
			melchoice = 0
			print "\nDo you want to create a free or a very structured melody?"
			while True: 
				melchoice = raw_input("enter 'f' for a free or 's' for a structured melody: ")
				if melchoice == "f": 
					break
				elif melchoice == "s": 
					break
				
			if str(melchoice) == "f": 
				freemel = True
			else: 
				freemel = False
			
			
			# create a free melody
			
			if freemel: 
			
				mel = []
				mel.append(musicSamplesMeasures[2])
				mel.append(musicSamplesMeasures[3])
				mel.append(musicSamplesMeasures[4])
				mel.append(musicSamplesMeasures[5])
			
				mel.append(musicSamplesMeasures[6])
				mel.append(musicSamplesMeasures[7])
				mel.append(musicSamplesMeasures[8])
				mel.append(musicSamplesMeasures[9])

				mel.append(musicSamplesMeasures[10])
				mel.append(musicSamplesMeasures[11])
				mel.append(musicSamplesMeasures[12])
				mel.append(musicSamplesMeasures[13])
			
				mel.append(musicSamplesMeasures[14])
				mel.append(musicSamplesMeasures[15])
				mel.append(musicSamplesMeasures[16])
				mel.append(musicSamplesMeasures[17])
			
				mel.append(musicSamplesMeasures[18])
				mel.append(musicSamplesMeasures[19])
				mel.append(musicSamplesMeasures[20])
				mel.append(musicSamplesMeasures[21])
			
				mel.append(musicSamplesMeasures[2])
				mel.append(musicSamplesMeasures[3])
				mel.append(musicSamplesMeasures[4])
				mel.append(musicSamplesMeasures[5])
			
				mel.append(musicSamplesMeasures[6])
				mel.append(musicSamplesMeasures[7])
				mel.append(musicSamplesMeasures[8])
				mel.append(musicSamplesMeasures[9])
			
				helper.resetContexts([intrOutro, mel])
			
				helper.combineSubparts(part, [mel], intrOutro)
			
			if not freemel: 
				
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
				bridge.append(musicSamplesMeasures[5])
		
				helper.resetContexts([intrOutro, verse, chorus, bridge])
			
				helper.combineSubparts(part, [verse, verse, chorus, verse, chorus, bridge, chorus], intrOutro)
			
				
				
			self._melodyFree = False
		
		#-----------------------------------------------------------------#
		# Drums
		
		elif partInstr.midiProgram in mididicts.instrumentGroups["rhythm"] or not self._melodyFree:
			musicSamplesMeasures = _createMeasuresWithLength(6)
			
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
			bridge.append(musicSamplesMeasures[2])
			
			helper.resetContexts([verse, chorus, bridge])
			
			helper.combineSubparts(part, [verse, verse, chorus, verse, chorus, bridge, chorus], restMeasure, numOfRepeats = 2)
		
		#-----------------------------------------------------------------#
		# all the rest
		
		else:
			musicSamplesMeasures = _createMeasuresWithLength(6)
			
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
			bridge.append(musicSamplesMeasures[2])
		
			helper.resetContexts([verse, chorus, bridge])
			
			helper.combineSubparts(part, [verse, verse, chorus, verse, chorus, bridge, chorus], restMeasure, numOfRepeats = 2)
		
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
		
		self._melodyFree = True

		
		for instrument in self._activeInstruments:
			logger.status("Generating part for %s." % instrument)
			# TODO determine measureNum and measureLen through analysis
			newPart = self._generatePart(instrument, measureNum, measureLen)
			
			# check and change conflicting notes
			e = 0
			while e < len(newPart):
				if not isinstance(newPart[e], music21.stream.Measure):
					e = e + 1
					continue
				newM = newPart[e]
				for oldPart in s:
					if not e < len(oldPart):
						continue
					oldM = oldPart[e]
					if isinstance(oldM, music21.ElementWrapper) and isinstance(oldM.obj, list):
						oldMList = oldM.obj
					else:
						oldMList = [oldM]
					for oldM in oldMList:
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
		# conflictlist = [1,11,13,23,25,35,37,47,49,59,61,71,73,83,85,95,97]
		
		# helmholzlist follows another theory. 
		#conflictlist = [1,2,10,11,13,14,22,23,25,26,34,35,37,38,46,47,49,50,58,59,61,62,70,71]

		# 16th century standard  
		conflictlist = [1,2,5,6,10,11,13,14,17,18,22,23,25,26,29,30,34,35,37,38,41,42,46,47,49,50,53,54,58,59,61,62,65,66,70,71]

		if Note1.isNote and Note2.isNote:
			intval = music21.interval.notesToChromatic(Note1,Note2)
			if intval.undirected in conflictlist: 
				return True
			else: 
				return False
		else: 
			return False