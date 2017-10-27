import sys
import random
import numpy.random as nrandom
import grammar_consts as gc
import argparse
import pickle
import nltk
from grammar_processor import NGramProcessor
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

	# # display info about imported data...
		# ngrams = processed.get_ngrams()
		# for ngram in ngrams.keys():
		# 	count = ngrams[ngram]
		# 	if (count > 1):
		# 		print(' '.join(ngram) + ": " + str(count))
		# print('num unique words: ' + str(len(processed.get_default()))) # num unique 

	# create phrases/sentences
	punct = gc.PUNCT
	for i in range(args.repeat):
		title = processed.generate(processed.root)
		title = title.replace(' ,', ',')
		title = title.replace(' .', '.')
		print(title)
	print('+-------------------------------------DONE-------------------------------------+')

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
		# What great day home may heaven this I heaven .
		# Stats: 7 ngram usages for 9 iterations.
		# 
		# Besides give presents I go straight up much however , let them lightly had better to table beside god to say singing 'come .
		# Stats: 20 ngram usages for 23 iterations. 
		# 
		# Besides , the leave where much people could father that I , you will come down till her deep close of we might strike while flower , after when a ulysses are held over till seats set sail and son arceisius .
		# Stats: 39 ngram usages for 41 iterations.
		#
		# Then my eye would soon see that a stone against troy , but perished even taking with myself where I doubted my courage .
		# Stats: 18 ngram usages for 23 iterations.
		#
		# When euryclea said she saw smoke of nine cities of yet another to relate the thigh iron- on deck on his gold lamp and divide my son behind about supper by their reckoning that hateful armour of your back .
		# Stats: 33 ngram usages for 39 iterations.
		# 
		# Run into ulysses both sail you greatly when menelaus heard .
		# Stats: 8 ngram usages for 10 iterations.
		#
		# But henceforth cruel bondage may heaven itself .
		# Stats: 5 ngram usages for 7 iterations.
		#
		# So drive down and welcome my sacrifice to our goods come round euryclea traders where minerva therefore talking our rest to geraestus , ocyalus vouchsafe the scylla off him , eurymachus in such another there ulysses some jutting suitors .
		# Stats: 27 ngram usages for 39 iterations.
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