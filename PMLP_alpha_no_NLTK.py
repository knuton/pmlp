#-----------------------------------------------------------------# 
#
# Name:		PMLP_alpha.py
# Purpose: 	generate a simple song
#
# Version: 	02.07.2010
#
#-----------------------------------------------------------------# 

#from pudb import set_trace

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


# ngramDistri is our frequency distribution of ngrams
ngramDistri = frequency.FrequencyDistribution(trigrams)

# determine the alphabet
alphabet = ngramDistri.samples()

# generate a new note (if possible based on its probability given a certain history)
def generator(history):
	# generate a random number between 0 and 1
	p = random.random()
	
	# look for a high probability for a trigram given the history and if found return the last note of that trigram
	for c in alphabet: 
		# c is a tuple of this form: ((x,y),z)
		# c[1] = z
		ngram = history, c[1] 
		p -= ngramDistri.relativeFrequency(ngram) # p - probability of c given history
		if p <= 0:
			return c[1]
	
	# if nothing is found take a random note
	warnings.warn("Failed to find random choice with remaining p = %g" % (p))
	alternative = random.choice(alphabet)
	return alternative[1]


# randomSong creates a new song (or rather a new Part)
def randomSong(ngramModel, startsequence, songlength, filename):
	# n is the order of the ngram (e.g. 3)
	#history = startsequence[len(startsequence)-n:len(startsequence)] 
	history = startsequence
	print "First History"
	print history
	
	# create list to fill with new notes
	generated = list()
 	
 	# fill the list with new notes
 	for elem in range(songlength): 
	
		# selects random note c with Pr(c|history)
		nextNote = generator(history)
		
		# add new note to list of generated notes
		generated.append(nextNote)
		
		# update history
		# This is only creates a trigram history -> has to be changed if other ngrams are used
		#history = (history[1], nextNote)
		
		history = history[1:n-1] + (nextNote,)
		print "New History"
		print history
		
	# add startsequence to song
	reversestart = []
	for elem in startsequence: 
		reversestart.insert(0, elem)
	
	for elem in reversestart:
		generated.insert(0, elem)

	# create new music21 stream using the generated notes
	# later it would be better to first generate an intro, then some in-between-stuff and finally an outro
	"""
	s = music21.stream.Stream()
	for note in generated:
		s.append(note)
	"""
	
	# this way we can insert different parts as soon as we got more than one 
	a = music21.stream.Part()
	for note in generated:
		a.append(note)
		
	s = music21.stream.Score()
	s.insert(0, a)
		
	# show new song
	#s.show('musicxml')
	
	# store new song in musicXML file
	s.write('musicxml', 'output/'+ str(filename) + '.xml')
	
	# Probleme bisher: 
	# - Kommt mit grossen Liedlaengen nicht klar
	# - Kuemmert sich noch gar nicht um Liedstruktur etc
	# - koennte noch Fehler bei der generate methode geben 
	# - Andere Dinge wie startkey, tempo, instrumente/spuren etc koennte/sollte man auch noch einfuegen
	
# so far start only consists of 2 arbitrary notes
# could be something more sophisticated like a real intro 
starttrigram = alphabet[3]
start = starttrigram[0]
print start

# choose a filename
songname = raw_input("Enter a name for the new song: ")

# create a new song 
randomSong(ngramDistri, start, 40, songname)

	
