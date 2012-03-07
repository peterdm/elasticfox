#!/bin/sh

curl -XDELETE 'localhost:9200/artist';

curl -XPUT 'localhost:9200/artist' -d '
{
   "settings": {
	"analysis": {
		"filter": {
			"phrase_ngrams": {
				"side": "front",
				"max_gram": 20,
				"min_gram": 1,
				"type": "edgeNGram" 
			}
		},
		"analyzer": {
			"full_phrase": {
				"type": "custom",
				"filter": [
					"lowercase",
					"asciifolding"
				],
				"tokenizer": "standard"
			},
			"partial_phrase": {
				"type": "custom",
				"filter": [
					"lowercase",
					"asciifolding",
					"phrase_ngrams"
				],
				"tokenizer": "standard"
			}
		}
	}
   },
   "mappings": {
	"artist": {
		"properties": {
			"id": {
				"type": "string",
				"store": "yes"
			},
			"title": {
				"boost": 1.0,
				"type": "multi_field",
				"fields": {
					"partial": {
						"type": "string",
						"search_analyzer": "full_phrase",
						"index_analyzer": "partial_phrase"
					},
					"title": {
						"type": "string",
						"analyzer": "full_phrase"
					}
				}
			},
			"context": {
				"index": "analyzed",
				"store": "yes",
				"type": "string"
			},
			"weight": {
				"store": "yes",
				"type": "float"
			},
			"disambig_number": {
				"store": "yes",
				"type": "integer"
			},
			"aliases": {
				"index": "analyzed",
				"store": "yes",
				"type": "string"
			}
		}
	}
   }
}'

