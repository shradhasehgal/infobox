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

requests.packages.urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}
english_to_hindi_data = []
overall={"data":[]}
with open('hindi_person_data.json') as f:
    for line in f:
        info = json.loads(line)
        if 'en_wikipedia_title' in info:
            english_to_hindi_data.append(['hi_wikipedia_title'])

with open('log_name_id.json') as f:
    hindi_dict = json.load(f)

fw = open('secondary_dataset.json', "w+")
hindi_data = hindi_dict['data']
count = 0
query1 = """SELECT DISTINCT ?lang ?name ?instanceLabel WHERE {
  VALUES (?person) {(wd:"""
  
query2=""")}
  ?article schema:about ?person;
           schema:inLanguage ?lang;
           schema:name ?name;
           schema:isPartOf [ wikibase:wikiGroup "wikipedia" ].
  ?person wdt:P31 ?instance .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  FILTER(?lang in ('en')).
  FILTER (!CONTAINS(?name, ':')).
}"""

for article in hindi_data:
    if article[1] not in english_to_hindi_data and 'श्रेणी' not in article[1]:
        # print(article[1])
        url = 'https://hi.wikipedia.org/w/api.php?action=query&prop=pageprops&titles='+article[1]+'&format=json'
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=5)
            # print(response.content)
            response_dict = ast.literal_eval(response.content.decode('utf-8'))
            for k,v in response_dict['query']['pages'].items():
                f = 0
                if 'wikibase_item' in v['pageprops']:
                    query = query1 + v['pageprops']['wikibase_item']+query2
                    results = get_results(endpoint_url, query)
                    # print(results)
                    try:
                        for result in results["results"]["bindings"]:
                            # print(result['instanceLabel']['value'])
                            if result['instanceLabel']['value'] == 'human':
                                print(result['name']['value'])
                                info_dict = {"en_wikipedia_title":result['name']['value'], "hi_wikipedia_title":article[1], "wd_id":v['pageprops']['wikibase_item']}
                                overall['data'].append(info_dict)
                                # fw.write(result['name']['value'] + ","+article[1]+"\n")
                                f = 1
                                count += 1
                                break
                    except:
                        print("Error 1")
                if f == 1:
                    break
        except:
            print("Error 2")
        sleep(1)

print(count)
json.dump(overall, fw)