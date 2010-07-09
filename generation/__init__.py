# --- Add parent dir to paths for doctest compatiable intra-package imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# --- End of parent loading

import music21.stream

import random

from statistics import ngram
from statistics import frequency
from tools import logger, music42
from common.exceptions import StateError

class Generator:
	""" Generates a new song from conditional frequency distributions. """
	
	def __init__(self, resultSet):
		""" Fills the generator with the available data. """
		self._melody = resultSet['melody']
		self._instruments = resultSet['instruments']
		self._bandSize = resultSet['bandSize']
		self._activeInstruments = self._instruments.topN(self._bandSize)
		self._alphabets = {}
		for instrument in self._activeInstruments:
			self._alphabets[instrument] = self._melody[instrument].sampleSpace
	
	def _generatePart(self, partName, measureNum, measureLen):
		""" Generates a part from its available data on call. """
		
		# Choose a random history as starting point
		history = random.choice(self._melody[partName].conditions)
		
		logger.status("Starting from " + str(history))
		
		score = list(history)
		
		# fill the score with new notes
		for i in range(measureNum): 
			
			# selects random note c with Pr(c|history)
			nextNote = self._predictNote(history, partName)
			
			# add new note to list of generated notes
			score.append(nextNote)
			
			history = history[1:] + (nextNote,)
			logger.status("Current history is " + str(history))
		
		part = music21.stream.Part()
		for note in score:
			part.append(note)
		
		return part
	
	def generate(self):
		s = music21.stream.Score()
		for instrument in self._activeInstruments:
			logger.status("Generating part for %s." % instrument)
			# TODO determine measureNum and measureLen through analysis
			s.insert(0, self._generatePart(instrument, 60, 4))
		return s
	
	def _completeMeasure(self, part, currQuarterLength, measureLength = 4):
		""" Fills up one measure worth of rests. """
		rest = music21.note.Rest()
		if currQuarterLength < measureLength:
			rest.quarterLength = measureLength - currQuarterLength
			part.append(rest)
			return part # TODO is this necessary? (used)
		elif currQuarterLength == measureLength:
			rest.quarterLength = measureLength
			part.append(rest)
			return part
	
	def _predictNote(self, realHistory, partName):
		""" Predicts the next note from a history that is being provided. """
		normalizedHistory = music42.normalizeNotes(realHistory)
		
		if self._melody[partName].expected(normalizedHistory):
			return music42.denormalizeNote(self._melody[partName].expectedFuzz(normalizedHistory), realHistory)
		
		# if nothing is found take a random note
		logger.log("Failed to find prediction for history %s" % (normalizedHistory,))
		return random.choice(self._alphabets[partName])
