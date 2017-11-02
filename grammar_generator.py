import sys
import random
import numpy.random as nrandom
import grammar_consts as gc
import argparse
import pickle
import nltk
from grammar_processor import GrammarProcessor
from grammar_processor import SentenceTree

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('inpath',
						help='Filepath of .pkl file to be read after text has been process with grammar_processor.py, by default in ./processed/filename.pkl')
	parser.add_argument('-l', '--length', type=int, default=10,
						help='Number of words to generate') # deprecated
	parser.add_argument('-r', '--repeat', type=int, default=10,
						help='Number of phrases of length l to generate')
	args = parser.parse_args()

	processed = None
	with open(args.inpath, 'rb') as processedData:
		processed = pickle.load(processedData)

	# create phrases/sentences
	print('\n' + gc.box('Printing ' + str(args.repeat) + ' sentences', gc.TERMINAL_WIDTH) + '\n')
	for i in range(args.repeat):
		title = processed.generate(processed.root).strip()
		for word in title.split():
			if word in gc.ME:
				title = title.replace(' ' + word + ' ', ' ' + word.title() + ' ')
		title = title.replace(' ,', ',')
		title = title.replace(' .', '.')
		print(title[:1].title() + title[1:] + '.\n')
	print(gc.box('DONE', gc.TERMINAL_WIDTH) + '\n')

	# Probably final formatting, like adding periods, title capitalization and so on,
		# should all be done here. The generate method should only return a lowercase
		# string without any punctuation at all. Fuck quotes btw.
		# TODO: Title mode arg which switches between printing modes,
		# 		Second filepath arg conditional on title mode giving path of titles file?
		#		...do I even want to formalize this?
		# with open('lovecraft_titles.txt') as file:
		# 	exact_names = list()
		# 	lines = file.readlines()
		# 	for line in lines:
		# 		exact_names.append(line.lower().strip())
		# 	i = 0
		# 	j = 0
		# 	while (i < args.repeat):
		# 		j += 1
		# 		title = processed.generate(processed.root).lower()
		# 		title = title.replace(' ,', ',')
		# 		title = title.replace(' .', '.')
		# 		if (((title.split('\n', 1)[0])) not in exact_names):
		# 			i += 1
		# 			print(title.title())
		# 	print('Total iterations before ' + str(args.repeat) + ' requested: ' + str(j))

	# Example outputs:
		# But henceforth cruel bondage may heaven itself .
		# Stats: 5 ngram usages for 7 iterations.
		#
		# Then she ran mountains, I myself, I cannot.
		# 
	# 
	# NOTE: really seems like it strongly approaches the text for the first several words,
	#		which would make sense given the large sample size of the tree at that point,
	#		then gets steadily worse as the sentence progresses and becomes longer.
	#		This could just be due to a sentence sounding more convincing the shorter it is,
	#		but the only way to find out really would be to get a massive amount of similar
	#		data -- way longer than The Odyssey.
	# 
	# Hilarious though when used as a title generator:
	# The Transition Of Dr Mystery S Martin.
	# The Rats In The Rats.
	# John, Dumb, And Blind.
	# The Monster Randolph.
	# The Evil Clergyman Randolph.
	# The Quest Of Randolph.
	# The Colour Out Of Juan.