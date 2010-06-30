#-----------------------------------------------------------------# 
#
# Name:		PMLP_alpha.py
# Purpose: 	generate a simple song
#
# Version: 	30.06.2010
#
#-----------------------------------------------------------------# 

import nltk.probability
from nltk.probability import *

import music21.corpus
import music21.stream

import corpus.persistence
from statistics import ngram
from statistics import frequency

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
			noteNGram = ngram.NoteNGram(sNT)
			trigrams.append((noteNGram.sequence[0:n-1], noteNGram.sequence[n-1]))
	# Skip for now
	# corpus.persistence.dump('melody', 'bach', trigrams)

freakyDistri = nltk.probability.ConditionalFreqDist(trigrams)


#Use MLE (no smoothing) to generate Probability Distribution:
ngramModel = ConditionalProbDist(freakyDistri, MLEProbDist)


# alphabet festlegen: 
# (aus statistics frequency.py)

ngramDistri = frequency.FrequencyDistribution(trigrams)

alphabet = ngramDistri.samples()


# _generate generiert zufaellige note aus alphabet
def _generate (self):
	p = random.random()
	for c in alphabet:
		p -= self.prob(c)
		if p <= 0:
			return c
	#warnings.warn("Failed to find random choice with remaining p=%g" % (p))
	return random.choice(alphabet)

ProbDistI.generate = _generate # this overrides the generate() method of ProbDistI objects

 
# randomSong creates a new song (or rather a new Part)
def randomSong(ngramModel, startsequence, songlength, filename):
	
	# n is the order of the ngram (e.g. 3)
	history = startsequence[len(startsequence)-n:len(startsequence)] 
	
	# create list to fill with new notes
	generated = list()
 	
 	for elem in range(songlength): 
		
		# probability distribution Pr(X | history) with class ProbDistI
		probGivenHistory = ngramModel[history]  
	
		# selects random note c with Pr(c|history)
		nextNote = probGivenHistory.generate() 
		
		generated.append(nextNote)
		
		# update history
		history = history[1:n] + nextNote 
		
	# add startsequence to song
	generated.reverse()
	generated.append(startsequence)
	generated.reverse()
	
	# create new music21 stream using the generated notes
	s = music21.stream.Stream()
	for note in generated:
		s.append(note)
	
	# show new song
	#s.show('musicxml')
	
	# store new song in musicXML file
	s.write('musicxml', 'output/'+ str(filename) + '.xml')
	
	
	# Probleme bisher: 
	# - Kommt mit grossen Liedlaengen nicht klar
	# - Kuemmert sich noch gar nicht um Liedstruktur etc
	# - koennte noch Fehler bei der generate methode geben 
	# - Andere Dinge wie startkey, tempo, instrumente/spuren etc koennte/sollte man auch noch einfuegen
	

# start sollte noch etwas professioneller z.B. durch Analyse der Liedanfaenge generiert werden
start =  alphabet[3],alphabet[4], alphabet[5]

# choose a filename
songname = raw_input("Enter a name for the new song: ")

# create a new song 
randomSong(ngramModel, start, 40, songname)

	
