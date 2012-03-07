'''
Created on Feb 6, 2012

@author: yoav

Basic POC methods skeleton for elasticsearch

'''

import pyes # http://pypi.python.org/pypi/pyes/
import csv
import subprocess # only for temporary dirty hack
import json

######## configuration parameters ########
SERVER = 'localhost'
PORT = '9200'
RAW_DATA_FILE = 'artist-test.tsv'
INDEX_NAME = 'artist'
DOC_TYPE = 'artist-test-doc-type'
SETUP_SCRIPT = './setup_artist.sh'

# Index SETTINGS -- Used to configure analysers, etc...  (es.update_settings)
SETTINGS = ''
#SETTINGS = {
#			u'analysis': {
#				u'filter': {
#					'title_ngrams': {
#						'side': 'front',
#						'max_gram': 20,
#						'min_gram': 1,
#						'type': 'edgeNGram' 
#					}
#				},
#				u'analyzer': {
#					'full_title': {
#						'type': 'custom',
#						'filter': [
#							'standard',
#							'lowercase',
#							'asciifolding'
#						],
#						'tokenizer': 'standard'
#					},
#					'partial_title': {
#						'type': 'custom',
#						'filter': [
#							'standard',
#							'lowercase',
#							'asciifolding',
#							'title_ngrams'
#						],
#						'tokenizer': 'standard'
#					}
#				}
#			}		
#}


# TODO: modify the mapping to represent the current schema
MAPPING = ''  # See setup_artist.sh for mapping info
#{ 
#			u'id' : {
#					u'store': u'yes',
#					u'type': u'string',
#			},
#			u'title': {
#					u'boost': 1.0,
#					u'type': u'multi_field',
#					u'fields': {
#							u'partial': {
#									u'type': u'string',
#									u'search_analyzer': u'full_phrase',
#									u'index_analyzer': u'partial_phrase'
#							},
#							u'title': {
#									u'type': u'string',
#									u'analyzer': u'full_phrase'
#							}
#					}
#			},
#			u'context' : {
#					u'index': u'analyzed',
#					u'store': u'yes',
#					u'type': u'string'
#			},
#			u'weight' : {
#					u'store': u'yes',
#					u'type': u'float'
#			},
#			u'disambig_number' : {
#					u'store': u'yes',
#					u'type': u'integer'
#			},
#			u'aliases' : {
#					u'index': u'analyzed',
#					u'store': u'yes',
#					u'type': u'string'
#			}
# 'type' conflicts with internal ES 'type' field -- if you want to handle this field specially, the name needs changing
#			u'type' : {
#					'store': 'yes',
#					'type': 'string'
#			},
#}

###########################################


######## helper functions ########
def deleteIndex(conn, indexName):
	try:
		conn.delete_index(indexName)
		print "deleting " + indexName
		return True
	except:
		return False

def createIndex(conn, indexName, deleteIfExists=False):
	#if deleteIfExists:
	#	deleteIndex(conn, indexName)
	
	print "creating " + indexName
	subprocess.call([SETUP_SCRIPT])
	
	#conn.create_index(indexName)

def createMapping(conn, indexName, docType, mapping):
	conn.put_mapping(docType, mapping, [indexName])

def updateSettings(conn, indexName, settings):
	conn.update_settings(indexName, settings)


def init(indexName, docType, mapping, settings):
	conn = pyes.ES(['%s:%s' % (SERVER, PORT)]) 
	createIndex(conn, indexName, deleteIfExists=False)
	#createMapping(conn, indexName, docType, mapping)
	#updateSettings(conn, indexName, settings)
	return conn

def printResult(rs):
	print "==================================="
	print "Query: %(query)s" % {"query":rs.query}
	print "-----------------------------------"
	print "Found %(total)d results" % {"total":rs.total}
	print "-----------------------------------"
	print "Facets: %(facets)r" % {"facets":rs.facets}
	print "==================================="
	for result in rs:
	  print result
	  print "..................................."
	print
	print

##################################


######## indexing and search functions ########


def index(conn, csvDataFile, indexName, docType):
	f = open(csvDataFile)

	dialect = csv.Sniffer().sniff(f.read(1024))
	f.seek(0)
	reader = csv.DictReader(f, dialect=dialect)	
	
	
	for i in reader:
		conn.index(i, indexName, docType)
	
def search(conn, query):
	#q = pyes.TermQuery("title", query)
	q = pyes.TermQuery("title", query)
	#q = pyes.Query()
	print q.serialize()
	
	result = conn.search(query=q)
	print result


def exactMatchSearch(conn, query):
	q = pyes.TextQuery("title", query, 'phrase')
	s = q.search() # get a search object
	s.facet.add_term_facet('type')
	printResult(conn.search(query=s))
		
def prefixingSearch(conn, query):
	q = pyes.TextQuery("title", query, 'phrase_prefix')
	s = q.search() # get a search object : pass start= and size= for scrolling
	
def ngramPrefixingSearch(conn, query):
	xq = pyes.TextQuery("title", query);
	pq = pyes.TextQuery("title.partial", query)
	
	q = pyes.BoolQuery()
	q.add_should(xq).add_should(pq)
	s = q.search()
	s.facet.add_term_facet('type')
	printResult(conn.search(query=s))

	
def interactiveQuery(conn, queryFunc):
	while True:
		q = raw_input('--> ')
		queryFunc(conn, q)

def chooseSearch():
	print ""
	print "Choose search type?"
	print "==================="
	print "1. Exact Match"
	print "2. Prefix Match"
	print "3. Prefix Match using Ngrams"

	choice = raw_input('>> ')

	if (choice=='1'): return exactMatchSearch
	elif (choice=='2'): return prefixingSearch
	elif (choice=='3'): return ngramPrefixingSearch
	else: return chooseSearch()



###############################################


######## main ########
if __name__ == '__main__':
	print "For now, create the index and custom analyzers first using setup_artist.sh"
	conn = init(INDEX_NAME, DOC_TYPE, MAPPING, SETTINGS)
	index(conn, RAW_DATA_FILE, INDEX_NAME, DOC_TYPE )
	conn.flush()

	queryFunc = chooseSearch()	
	interactiveQuery(conn, queryFunc)
######################
