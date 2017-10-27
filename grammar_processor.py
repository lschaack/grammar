# __init__ and count methods started from:
# http://www.decontextualize.com/teaching/dwwp/topics-n-grams-and-markov-chains/
import sys
import random
import numpy.random as nrandom
import nltk
import grammar_consts as gc
import argparse
import pickle

class NGramProcessor(object):
	# n is the n in ngrams
	# inputString is a formatted string stripped of newlines and with spaces between punctuation
	# TODO: use a less hack-y method to get starters
	def __init__(self, n, inputString, sentences, senTree):
		self.n = n				# the n in  n-grams
		self.ngrams = dict()	# counts of n-grams
		self.starters = dict()	# from sentence-starting words to their respective integer counts
		self.tags = dict()		# from word to list of strings representing corresponding POS
		self.default = dict() 	# inverse tags now, from POS to words
		self.counts = dict()
		self.root = senTree 	# starting node of the sentence parse tree
		print(inputString[0:1000] + '...') # for verification of chosen text, formatting visibility
		self.process(inputString, sentences)
		self.start = self.get_prob_dict(self.starters)

	# make this more efficient so that everything is performed in a single loop
	# currently three steps:
	# 1. populate the default dictionary containing counts of individual words
	# 2. tag each word in each sentence with its part of speech
	# 3. populate list of ngrams
	def process(self, inputString, sentences):
		tokens = inputString.split()
		# populate default dictionary
		self.count_tokens(tokens)
		self.build_sentence_tree(sentences)
		# populate self.ngrams 
		for i in range(len(tokens) - self.n + 1):
			gram = tuple(tokens[i:(i + self.n)])
			gc.add_to_dict(self.ngrams, gram)

	# sort of slightly deprecated, but need the starters thing
	def count_tokens(self, tokens):
		nextIsStarter = 1 # first word starts the first sentence
		for token in tokens:
			gc.add_to_dict(self.counts, token)
			if (nextIsStarter):
				gc.add_to_dict(self.starters, token)
				nextIsStarter = 0
			elif (token in gc.INTERSENTENCE_PUNCT):
				nextIsStarter = 1		

	# build the sentence parsing tree, that is:
	# a tree where each branch represents the parts of speech corresponding to . . .
	# an observed sequence of words within a sentence within the text
	def build_sentence_tree(self, sentences):
		for sentence in sentences:
			# tokens = nltk.word_tokenize(sentence)
			tokens = sentence.split() # this keeps conjunctions, which is easier to process naively
			tagged = nltk.pos_tag(tokens)
			currNode = self.root # reset for each new sentence
			for tag in tagged:
				self.add_tag(tag[0], tag[1])
				if (tag[1] not in self.default.keys()): # make sure an entry exists for the tag
					self.default[tag[1]] = dict()
				gc.add_to_dict(self.default[tag[1]], tag[0])
				currNode.insert(tag[1])
				currNode = currNode.branches[tag[1]] # get next node in tree
		# print('printing tree...')
		# print(self.root.toString())

	# given previous word in the output, returns probabilistically chosen next word
	def generate(self, node, prev = '', i = 0, nNgramUse = 0):
		if (not prev or prev in gc.INTERSENTENCE_PUNCT):
			start = self.choose_start()
			while(start == '.'):
				start = self.choose_start() # incredibly hack-y and bad, change this
			startTag = self.tags[start.lower()][0] # get the first POS of chosen starting word
			nextNode = self.root.branches[startTag] 
			return start.title() + ' ' + self.generate(nextNode, start, i + 1, nNgramUse)
		else:
			options = dict()
			for option in node.branches.keys():
				options[option] = node.branches[option].freq
			options = self.get_prob_dict(options)
			if (not options):
				return '.\nStats: ' + str(nNgramUse) + ' ngram usages for ' + str(i) + ' iterations.\n'
			# choose a POS from the tree based on frequency
			option = nrandom.choice(list(options.keys()), p=list(options.values()))
			# possibilities = self.choose_default(options)
			possibilities = self.default[option]
			ngram_poss = self.grab_possibilities(prev)
			combined = set(possibilities.keys()) & set(ngram_poss.keys())
			prob_poss = None
			if (combined):
				# https://stackoverflow.com/questions/6505008/dictionary-keys-match-on-list-get-key-value-pair
				comb_poss = {k: ngram_poss[k] for k in combined if k in ngram_poss} # get the counts too, very hack-y
				prob_poss = self.get_prob_dict(comb_poss)
				nNgramUse += 1
			else:
				prob_poss = self.get_prob_dict(possibilities)
			# chooses from all possibilities based on associated probabilities
			nextWord = nrandom.choice(list(prob_poss.keys()), p=list(prob_poss.values()))
			# get common element between chosen word and options, from jamylak's answer at:
			# https://stackoverflow.com/questions/16118621/first-common-element-from-two-lists/16118989#16118989
			tag_set = set(self.tags[nextWord.lower()])
			pos = next((a for a in options if a in tag_set), None)
			# capitalize 'i's
			if (nextWord in gc.ME):
				nextWord = nextWord.title()
			nextNode = node.branches[pos]
			return nextWord + ' ' + self.generate(nextNode, nextWord, i + 1, nNgramUse)

	def add_tag(self, word, pos):
		if (word in self.tags.keys()):
			if (pos not in self.tags[word]):
				self.tags[word].append(pos)
		else:
			self.tags[word] = [pos]

	def grab_possibilities(self, prev):
		result = dict()
		for key in self.ngrams.keys():
			if (key[0] == prev):
				gc.add_to_dict(result, key[1])
		return result

	def choose_default(self, options):
		possibilities = dict()
		for option in options:
			possibilities.update(self.default[option])
		return possibilities

	# choose from any word which started a sentence in the original text
	def choose_start(self):
		return nrandom.choice(list(self.start.keys()), p=list(self.start.values()))

	# given a dictionary from any key to number values, returns a dictionary from
	# same keys to calculated probabilities as values 
	def get_prob_dict(self, dictionary):
		total = sum(dictionary.values())
		result = dict()
		for key in dictionary.keys():
			result[key] = dictionary[key] / total
		return result

	def get_ngrams(self):
		return self.ngrams

	def get_starters(self):
		return self.starters

	def get_start(self):
		return self.start

	def get_default(self):
		return self.default

	def get_counts(self):
		return self.counts

	def get_tags(self):
		return self.tags

	def get_root(self):
		return self.root

# Turns a multi-line file into one long line with splits on punctuation.
class Formatter(object):
	def __init__(self, address):
		self.formatted = ''
		self.sentences = list()
		# extract lines from file to format
		file = open(address)
		lines = file.readlines()
		file.close()
		self.formatted = self.format_lines(lines)
		self.sentences = self.create_sents(self.formatted)

	def format_lines(self, lines):
		final = ''
		for line in lines:
			tokens = line.lower().strip().split()
			# check for punctuation and split on that
			for token in tokens:
				i = tokens.index(token)
				self.check_punct(tokens, token, i)
			# add tokens in the form of a line to a string
			newLine = ' '.join(tokens)
			final += newLine + ' '
		return final

	def check_punct(self, tokens, token, i):
		tokens[i] = tokens[i].replace('“', '"')
		tokens[i] = tokens[i].replace('”', '"')
		tokens[i] = tokens[i].replace('‘', '\'')
		tokens[i] = tokens[i].replace('’', '\'')
		# here, eventually actually handle quotes instead of just getting rid of them
		tokens[i] = tokens[i].strip('\'')
		tokens[i] = tokens[i].strip('\"')
		# make sure not checking punctuation, otherwise infinite loop
		if (tokens[i][-1:] in gc.PUNCT and len(token) > 1):
			# break into two grams (so ['becomes,'] becomes ['becomes', ','])
			tokens.insert(i + 1, (tokens[i])[-1:])
			tokens[i] = (tokens[i])[:-1]

	def create_sents(self, inputString):
		sentences = list()
		sentence = ''
		words = inputString.split()
		for word in words:
			if (word in gc.INTERSENTENCE_PUNCT):
				# complete sentence, add to sentences and restart
				sentences.append(sentence)
				sentence = ''
			else:
				sentence += ' ' + word # might have fencepost issue here
		return sentences

	def get_formatted(self):
		return self.formatted

	def get_sentences(self):
		return self.sentences

# idea from http://www.openbookproject.net/thinkcs/python/english2e/ch21.html
# tree with each node containing:
#	a string representing a part of speech (POS)
# 	a frequency representing num times that particular POS has been seen at that location in a sentence
#	a dictionary from POS strings to other SentenceTree nodes
# idea is: use as parse tree representing every sequence of P(s)OS seen in a text and with what freq.
class SentenceTree(object):
	def __init__(self, data = 'START', freq = 1):
		self.data = data
		self.freq = freq
		self.branches = dict()

	def insert(self, pos): # pos = part of speech
		if (self.branches.get(pos)):
			node = self.branches[pos]
			node.freq += 1
		else:
			self.branches[pos] = SentenceTree(data = pos)

	# different name convention for different print usage, making Java method comparison
	def toString(self, level = 0):
		ret = " " * level + repr(self.data) + ': '+ str(self.freq) + "\n"
		if (True): # (level < 10):
			for branch in self.branches.values():
				ret += branch.toString(level + 1)
		return ret

	def __str__(self):
		return ('{' + 'data = ' + str(self.data) + ', freq = ' + str(self.freq) + '}')

	def __repr__(self):
		return '<tree node representation>'

# end result: object with count of each ngram, count of individual words, and list of sentence-starting words

# TODO:
# Use actual bigram model w/chi-squared and things
# Improve space, time efficiency

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('filepath')
	parser.add_argument('-o', '--outname', default='output',
						help='Filename for output, so -o=innsmouth will write to ./processed/innsmouth.pkl')
	parser.add_argument('-n', '--ngram', type=int, default=3,
						help='Number of _grams to read, 2 = bigram, 3 = trigram, etc.')
	args = parser.parse_args()

	# eventually check if valid filepath
	formatter = Formatter(args.filepath)
	formatted = formatter.get_formatted()
	sentences = formatter.get_sentences()
	senTree = SentenceTree() # root of final sentence tree
	processed = NGramProcessor(args.ngram, formatted, sentences, senTree)
	ngrams = processed.get_ngrams()
	# for ngram in ngrams.keys():
	# 	count = ngrams[ngram]
	# 	if (count > 1):
	# 		print(' '.join(ngram) + ": " + str(count))
	print('+-------------------------------------DONE-------------------------------------+')
	print('Number of unique words: ' + str(len(processed.get_counts())))
	# print(processed.get_starters())
	# print(processed.get_default())
	# print(processed.get_tags())

	# save the object for use by the generator
	with open('./processed/' + args.outname + '.pkl', 'wb') as outpath:
		pickle.dump(processed, outpath)