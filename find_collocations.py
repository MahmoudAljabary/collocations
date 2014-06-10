#coding=utf-8

#########################################
# This code imports raw text, tokenizes it based on white space, and then generates a list of collocations
# according to a number of different parameters provided by the user at the command line.  -RPC, 4/1/2013
#
# Stopwords are filtered by default.  To obtain results which do not filter stopwords, alter script function.
#
# To find overlap of results from different measures/stat_methods, use other script.
##########################################

import nltk
from sys import *
import codecs
import os
from decimal import *
from optparse import OptionParser
from nltk.collocations import *
from nltk.probability import *
from nltk.util import *
from nltk.text import *

# parameters at command line
# input_file should be tokenized, one token per line formatting, such as underscored.x.corpus.txt
# ngram_size should either be "bigrams" or "trigrams"
# "stat_method" options include: pmi, likelihood_ratio, jaccard, poisson_stirling, student_t, chi_sq, dice, mi_like, and raw_freq

# Decide whether to include commmand line argument for association measure, omit for now
script, input_file, stopwords_file, ngram_size, stat_method, topN, win_size = argv
#script, input_file, stopwords_file, ngram_size, topN, win_size = argv



# define how text will be tokenized
tokenize_string = u'[`;\\\{}\u061b\u061f\u066a\u066b\u066c\u066d\u00b7\u00ab\u00bb\u201c\u201d\*\'\"()\.:,\s/\]\[\u200f\u060c=\-\+\|!]'

# read in raw data and perform tokenization
def read_in_data(filename):
	print "Reading in data file..."
	input_text = codecs.open(filename, 'r', encoding='utf-8')
	raw = input_text.read()
	tokens = nltk.regexp_tokenize(raw, tokenize_string, True)
	words = []
	# perform some processing on the words, such as stripping off newlines
	for token in tokens:
		newline = token.rstrip()
		words.append(newline)
	#print words[:5]
	return words

# read in stopwords for use in filtering
def read_in_stopwords(filename):
	print "Reading in stopwords..."
	input_file = codecs.open(filename,'r', encoding='utf-8')
	linesStop = input_file.readlines()
	stopwords = []
	for line in linesStop:
		newline = line.rstrip()
		stopwords.append(newline)
	return stopwords

# set up measures, mostly because I can't figure out how to coerce command line arg string to nltk ref
bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

pmi_bi = [bigram_measures.pmi,'pmi']
likelihood_ratio_bi = [bigram_measures.likelihood_ratio,'likelihood_ratio']
jaccard_bi = [bigram_measures.jaccard,'jaccard']
poisson_stirling_bi = [bigram_measures.poisson_stirling, 'poisson_stirling']
student_t_bi = [bigram_measures.student_t,'student_t']
chi_sq_bi = [bigram_measures.chi_sq,'chi_sq']
dice_bi = [bigram_measures.dice,'dice']
mi_like_bi = [bigram_measures.mi_like,'mi_like']
raw_freq_bi = [bigram_measures.raw_freq,'raw_freq']

pmi_tri = trigram_measures.pmi
likelihood_ratio_tri = trigram_measures.likelihood_ratio
jaccard_tri = trigram_measures.jaccard
poisson_stirling_tri = trigram_measures.poisson_stirling
student_t_tri = trigram_measures.student_t
chi_sq_tri = trigram_measures.chi_sq
dice_tri = bigram_measures.dice
mi_like_tri = trigram_measures.mi_like
raw_freq_tri = trigram_measures.raw_freq

bigram_methods = [pmi_bi, likelihood_ratio_bi, jaccard_bi, poisson_stirling_bi, student_t_bi, chi_sq_bi, dice_bi, mi_like_bi, raw_freq_bi]

trigram_methods = [pmi_tri, likelihood_ratio_tri, jaccard_tri, poisson_stirling_tri, student_t_tri, chi_sq_tri, dice_tri, mi_like_tri, raw_freq_tri]

# functions to calculate bigrams and trigrams
def topN_contiguous_bigrams(words, topN, measure):
	print "Finding collocations..."
	finder = BigramCollocationFinder.from_words(words)
	# Filter stopwords
	print "Applying word filter..."
	finder.apply_word_filter(lambda w: w in (stopwords))
	# Filter rare forms/ hapax legomena
	finder.apply_freq_filter(5)
	print "Calculating bigrams..."
	# Might need to find alternate way to reference measures, ditto for all functions below
	top_bigrams = finder.nbest(measure, topN)
	return top_bigrams

def topN_contiguous_trigrams(words, topN, measure):
	finder = TrigramCollocationFinder.from_words(words)
	# Filter stopwords
	finder.apply_word_filter(lambda w: w in (stopwords))
	print "Calculating trigrams..."
	top_trigrams = finder.nbest(measure, topN)
	return top_trigrams

def topN_noncontiguous_bigrams(words, topN, measure, window):
	finder = BigramCollocationFinder.from_words(words, window_size = window)
	# Filter stopwords
	finder.apply_word_filter(lambda w: w in (stopwords))
	print "Calculating bigrams..."
	top_bigrams = finder.nbest(measure, topN)
	return top_bigrams

def topN_noncontiguous_trigrams(words, topN, measure, window):
	finder = TrigramCollocationFinder.from_words(words, window_size = window)
	# Filter stopwords
	finder.apply_word_filter(lambda w: w in (stopwords))
	print "Calculating trigrams..."
	top_trigrams = finder.nbest(measure, topN)
	return top_trigrams

def main(input_file, stopwords_file, ngram_size, stat_method, topN, win_size):
	# set up base data
	print "Reading in data..."
	words = read_in_data(input_file)
	print "Total words (tokens): "+str(len(words))
	print "Reading in stopwords..."
	stopwords = read_in_stopwords(stopwords_file)

	# generate FreqDists for bigrams and trigrams
	bigrams = bigrams(words)
	print "Total unique bigrams: "+str(len(set(bigrams)))
	print "Building Bigram FreqDict..."
	fdist_bigrams = FreqDist(bigrams)
	trigrams = trigrams(words)
	print "Total unique trigrams: "+str(len(set(trigrams)))
	#print "Building Trigram FreqDict..."
	#fdist_trigrams = FreqDist(trigrams)

	# set up output files for displaying results
	output_contiguous = codecs.open('%s_%s_%s_%s.txt' % (input_file, ngram_size, stat_method, topN), 'w', encoding='utf-8')
	output_noncontiguous = codecs.open('%s_%s_%s_%s_%s.txt' % (input_file, ngram_size, stat_method, topN, win_size), 'w', encoding='utf-8')

	# generate bigrams or trigrams based on "ngram_size" argument at command line and dump into file

	if ngram_size == "bigrams":
		#for method in bigram_methods:
		#	 if method[1] == stat_method:
		#		topContBigrams = topN_contiguous_bigrams(words, topN, method[0])
		#		topNoncontBigrams = topN_noncontiguous_bigrams(words, topN, method[0], win_size)
		topContBigrams = topN_contiguous_bigrams(words, topN, bigram_measures.likelihood_ratio)
		#topNoncontBigrams = topN_noncontiguous_bigrams(words, topN, bigram_measures.likelihood_ratio, win_size)
		for bigram in topContBigrams:
			temp = ' '.join(bigram)
			output_contiguous.write((temp)+'\t'+(str(fdist_bigrams[bigram])+'\n'))

	if ngram_size == "trigrams":
		topContTrigrams = topN_contiguous_trigrams(words, topN, stat_method)
		topNoncontTrigrams = topN_noncontiguous_trigrams(words, topN, stat_method, win_size)
		for trigram in topContTrigrams:
			temp = ' '.join(trigram)
			output_contiguous.write((temp)+'\t'+(str(fdist_trigrams[trigram])+'\n'))

if __name__ == '__main__':
    main()
