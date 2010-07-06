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
		self._alphabet = self._melody.sampleSpace
	
	def generate(self):
		""" Generates a song from its available data on call. """
		# Replace this with data from analysis
		songlength = 50
		
		# Choose a random history as starting point
		history = random.choice(self._melody.conditions)
		
		logger.status("Starting from " + str(history))
		
		score = list(history)
		
		# fill the score with new notes
		for i in range(songlength): 
			
			# selects random note c with Pr(c|history)
			nextNote = self._predictNote(history)
			
			# add new note to list of generated notes
			score.append(nextNote)
			
			history = history[1:] + (nextNote,)
			logger.status("Current history is " + str(history))
		
		# this way we can insert different parts as soon as we got more than one 
		a = music21.stream.Part()
		for note in score:
			a.append(note)
		
		s = music21.stream.Score()
		s.insert(0, a)
		
		return s
	
	def _predictNote(self, realHistory):
		""" Predicts the next note from a history that is being provided. """
		normalizedHistory = music42.normalizeNotes(realHistory)
		
		if self._melody.expected(normalizedHistory):
			return music42.denormalizeNote(self._melody.expectedFuzz(normalizedHistory), realHistory)
		
		# if nothing is found take a random note
		logger.log("Failed to find prediction for history %s" % (normalizedHistory,))
		return random.choice(self._alphabet)