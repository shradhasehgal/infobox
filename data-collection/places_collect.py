import json
import requests
from time import sleep
import ast
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

endpoint_url = "https://query.wikidata.org/sparql"

query1 = """SELECT DISTINCT ?city ?cityLabel WHERE {
 {?city wdt:P31/wdt:P279* wd:Q515 .}
  UNION
 {?city wdt:P31/wdt:P279* wd:Q7275 .}
  UNION
  {?city wdt:P31/wdt:P279* wd:Q3957 .}
   SERVICE wikibase:label { bd:serviceParam wikibase:language "hi". }
}
"""

query2="""SELECT DISTINCT ?location ?locationLabel WHERE {
  {?location wdt:P31/wdt:P279* wd:Q79007 .
  ?location wdt:P17 wd:Q668 .}
  UNION
  {?location wdt:P31/wdt:P279* wd:Q532 .
   ?location wdt:P17 wd:Q668 .
  }
  UNION
  {?location wdt:P31/wdt:P279* wd:Q3624078.}
  
   SERVICE wikibase:label { bd:serviceParam wikibase:language "hi". }
}"""
overall = {"data": []}
ok = []
fw = open('places_dataset_2.json', "w+")
count = 0
results = get_results(endpoint_url, query1)
try:
    for result in results["results"]["bindings"]:
        # print(result)
        if 'xml:lang' in result['cityLabel']:
            info_dict = {"hi_wikipedia_title": result['cityLabel']['value'], "wd_id":result['city']['value'].strip('http://www.wikidata.org/entity/')}
            print(info_dict)
            count += 1
            overall['data'].append(info_dict)
except:
    print("Error 1")

sleep(10)
results = get_results(endpoint_url, query2)
try:
    for result in results["results"]["bindings"]:
        # print(result)
        if 'xml:lang' in result['locationLabel']:
            info_dict = {"hi_wikipedia_title": result['locationLabel']['value'], "wd_id":result['location']['value'].strip('http://www.wikidata.org/entity/')}
            print(info_dict)
            count += 1
            overall['data'].append(info_dict)
except:
    print("Error 1")

print(count)
json.dump(overall, fw)