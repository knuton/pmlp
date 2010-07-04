#-----------------------------------------------------------------# 
#
# Name:    brave_new_world.py
# Purpose: generate a simple song
#
# Version: 03.07.2010
#
#-----------------------------------------------------------------# 

import nltk.probability
from nltk.probability import *

import music21.corpus
import music21.stream

import corpus.persistence
from statistics import ngram
from statistics import frequency
from tools import logger, music42

import sys, random, warnings

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
			trigrams.append(ngram.NoteNGram(sNT))
			
	corpus.persistence.dump('melody', 'bach', trigrams)


# ngramDistri is our frequency distribution of ngrams
ngramCFD = frequency.ConditionalFrequencyDistribution([noteNGram.conditionTuple for noteNGram in trigrams])

# determine the alphabet
alphabet = ngramCFD.sampleSpace

# generate a new note (if possible based on its probability given a certain history)
def generator(realHistory):
	
	normalizedHistory = music42.normalizeNotes(realHistory)
	
	if ngramCFD.expected(normalizedHistory):
		return music42.denormalizeNote(ngramCFD.expectedFuzz(normalizedHistory), realHistory)
	
	# if nothing is found take a random note
	logger.log("Failed to find random choice for history %s" % (normalizedHistory,))
	return random.choice(alphabet)


# randomSong creates a new song (or rather a new Part)
def randomSong(ngramModel, startsequence, songlength, filename):
	# n is the order of the ngram (e.g. 3)
	n = len(startsequence)
	#history = startsequence[len(startsequence)-n:len(startsequence)] 
	history = startsequence
	print "First History"
	print history
	
	# create list to fill with new notes
	generated = list(startsequence)
	
	# fill the list with new notes
	for elem in range(songlength): 
	
		# selects random note c with Pr(c|history)
		nextNote = generator(history)
		
		# add new note to list of generated notes
		generated.append(nextNote)
		
		# update history
		# This is only creates a trigram history -> has to be changed if other ngrams are used
		#history = (history[1], nextNote)
		
		history = history[1:] + (nextNote,)
		print "New History"
		print history
	
	# this way we can insert different parts as soon as we got more than one 
	a = music21.stream.Part()
	for note in generated:
		a.append(note)
		
	s = music21.stream.Score()
	s.insert(0, a)
		
	# show new song
	s.show()
	
	# store new song in musicXML file
	# s.write('musicxml', 'output/'+ str(filename) + '.xml')
	
	# Probleme bisher: 
	# - Kommt mit grossen Liedlaengen nicht klar
	# - Kuemmert sich noch gar nicht um Liedstruktur etc
	# - koennte noch Fehler bei der generate methode geben 
	# - Andere Dinge wie startkey, tempo, instrumente/spuren etc koennte/sollte man auch noch einfuegen
	
# so far start only consists of 2 arbitrary notes
# could be something more sophisticated like a real intro 
start = random.choice(ngramCFD.conditions)
logger.log(start)

# choose a filename
songname = raw_input("Enter a name for the new song: ")

# create a new song 
randomSong(ngramCFD, start, 40, songname)

