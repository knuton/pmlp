import music21.corpus
import music21.environment

import datetime

import corpus
import training
import generation
from tools import logger

logo = """                                    ___ 
                 .__               |___|
  ______   _____ |  | ______      _|  _|
  \____ \ /     \|  | \____ \    (@) (@)
  |  |_> >  Y Y  \  |_|  |_> >          
  |   __/|__|_|  /____/   __/           
  |__|         \/     |__|              """

def startup():
	print logo
	menu()

def menu():
	choice = 0
	while not choice in ['l', 'g', 'h', 'q']:
		print "\n  $ MENU\n"
		print "  (l) List corpora"
		print "  (g) Generate a song"
		print "  (h) Help"
		print "  (q) Quit\n"
		try:
			choice = str(raw_input("  Make your choice by entering one of l, g, h and q > "))
		except ValueError:
			print "  Please enter an item's number."
	
	if choice == 'q':
		exit(0)
	elif choice == 'h':
		print "  We will add a help text later. Purhaps."
		menu()
	elif choice == 'g':
		collectionName = None
		corpusName = None
		xmls = []
		while not collectionName in ['pmlp', 'music21']:
			collectionName = str(raw_input("  Generate from a PMLP (`pmlp`) or music21 (`music21`) corpus? (Abort with `a`) > "))
			if collectionName == 'pmlp':
				corpusName = chooseCorpus('pmlp')
				xmls = corpus.getCollection(corpusName)
			elif collectionName == 'music21':
				corpusName = chooseCorpus('music21')
				xmls = music21.corpus.getComposer(corpusName)
			elif collectionName == 'a':
				break
		if corpusName:
			generate(collectionName, corpusName, xmls)
		menu()
	elif choice == 'l':
		listCorpora()
		raw_input("\n  Enter to return to menu.")
		menu()

def listCorpora(selected = None):
	if not selected:
		print '\n  $ CORPORA'
	
	if not selected or selected == 'pmlp':
		print "\n  $$ PMLP\n"
		pmlpCorpora = corpus.listCollections()
		for i in range(0, len(pmlpCorpora)):
			print "  " + str(i + 1) + ". " + str(pmlpCorpora[i]), not selected and "(PMLP)" or ''
		if selected:
			return pmlpCorpora
	if not selected or selected == 'music21':
		print "\n  $$ music21\n"
		music21Corpora = [composer[0] for composer in music21.corpus.COMPOSERS]
		for i in range(0, len(music21Corpora)):
			print "  " + str(i + 1) + ". " + str(music21Corpora[i]),  not selected and "(music21)" or ''
		if selected:
			return music21Corpora
	
	return []

def chooseCorpus(selected):
	if not selected:
		raise ValueError('Need to select a corpus collection.')
	
	choice = None
	possibilities = listCorpora(selected)
	
	while not choice in possibilities:
		if not choice == None:
			print "\n  Please enter the name of the corpus."
		choice = str(raw_input("\n  Which corpus should be used? > "))
	return choice

def generate(collection, corpus, xmls):
	print ""
	logger.status("Starting analysis.")
	trainer = training.Trainer(collection, corpus, xmls)
	trainer.run()
	logger.status("Finished analysis.")
	logger.status("Starting generation.")
	generator = generation.Generator(trainer.results)
	
	again = 'a'
	while again == 'a':
		song = generator.generate()
	
		song.write('musicxml', '%s_%s_%s.xml' % (collection, corpus, datetime.datetime.now().isoformat()))
		try:
			song.show()
		except music21.environment.EnvironmentException:
			logger.journal("Couldn't use show method to display generated score.")
		again = str(raw_input("  `a` to create another, anything else to exit to menu > "))

if __name__ == '__main__':
	startup()