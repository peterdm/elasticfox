curl -XPUT 'http://107.22.137.196:9200/test/?pretty=1'  -d '
{
   "mappings" : {
      "member" : {
         "properties" : {
            "location" : {
               "type" : "geo_point"
            },
            "member_id" : {
               "type" : "string",
               "analyzer" : "simple"
            },
            "birthday" : {
               "format" : "yyyy-MM-dd",
               "type" : "date"
            },
            "last_name" : {
               "fields" : {
                  "metaphone" : {
                     "type" : "string",
                     "analyzer" : "name_metaphone"
                  },
                  "partial" : {
                     "search_analyzer" : "full_name",
                     "index_analyzer" : "partial_name",
                     "type" : "string"
                  },
                  "last_name" : {
                     "type" : "string",
                     "analyzer" : "full_name"
                  }
               },
               "type" : "multi_field"
            },
            "first_name" : {
               "fields" : {
                  "metaphone" : {
                     "type" : "string",
                     "analyzer" : "name_metaphone"
                  },
                  "partial" : {
                     "search_analyzer" : "full_name",
                     "index_analyzer" : "partial_name",
                     "type" : "string"
                  },
                  "first_name" : {
                     "type" : "string",
                     "analyzer" : "full_name"
                  }
               },
               "type" : "multi_field"
            }
         }
      }
   },
   "settings" : {
      "analysis" : {
         "filter" : {
            "name_ngrams" : {
               "side" : "front",
               "max_gram" : 10,
               "min_gram" : 1,
               "type" : "edgeNGram"
            },
            "name_metaphone" : {
               "replace" : false,
               "encoder" : "metaphone",
               "type" : "phonetic"
            }
         },
         "analyzer" : {
            "full_name" : {
               "filter" : [
                  "standard",
                  "lowercase",
                  "asciifolding"
               ],
               "type" : "custom",
               "tokenizer" : "standard"
            },
            "name_metaphone" : {
               "filter" : [
                  "name_metaphone"
               ],
               "type" : "custom",
               "tokenizer" : "standard"
            },
            "partial_name" : {
               "filter" : [
                  "standard",
                  "lowercase",
                  "asciifolding",
                  "name_ngrams"
               ],
               "type" : "custom",
               "tokenizer" : "standard"
            }
         }
      }
   }
}
'

### INDEX SAMPLE DATA

# [Mon Jul 18 11:50:54 2011] Protocol: http, Server: 192.168.5.103:9200
curl -XPOST 'http://107.22.137.196:9200/_bulk?pretty=1'  -d '
{"index" : {"_index" : "test", "_type" : "member"}}
{"location" : [51.50853, -0.12574], "member_id" : "ABC-1234", "birthday" : "1970-10-24", "last_name" : "Smith", "first_name" : "Robert"}
{"index" : {"_index" : "test", "_type" : "member"}}
{"location" : [53.41667, -2.25], "member_id" : "ABC-1235", "birthday" : "1975-11-03", "last_name" : "Jones", "first_name" : "Robin"}
{"index" : {"_index" : "test", "_type" : "member"}}
{"location" : [41.3873, 2.1762], "member_id" : "ABC-1235", "birthday" : "1975-11-03", "last_name" : "Sánchez", "first_name" : "Jordi"}
'
