#!/usr/bin/env python
# coding: utf-8

# ### Method 1

# In[ ]:


import sys
from qwikidata.sparql import return_sparql_query_results
from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api
from SPARQLWrapper import SPARQLWrapper, JSON
import json
from tqdm import tqdm
import re
import requests as r
import pandas as pd
from collections import defaultdict
from libindic import inexactsearch
import pandas as pd
sys.path.append('../method2')
from People_translator import Translation_Api
translator = Translation_Api()


# In[ ]:


properties = {
    "name": "P2561",
    "native_name": "P1559",
    "image": "P18",
    "flag": "P163",
    "map": "P242",
    "motto":"P1546",
    "timezone": "P2907",
    "country": "P17",
    "location": "P276",
    "area / area_km2": "P2046",
    "length / length_km": "P2043",
    "width / width_km": "P2049",
    "population": "P1082",
    "elevation / elevation_m":"P2044" ,
    "geology" : "P2695",
}

to_transliteration = ['motto']


# In[ ]:


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

endpoint_url = "https://query.wikidata.org/sparql"


# In[ ]:


#calls qwikidata get entity function for an entity id
def getEntityInfo(eid):
    return get_entity_dict_from_api(eid)

#extract the name of the entity or the property value in native language
def extractName(info):
    return info.get('labels', {}).get('en', {}).get('value', "")

#extract the description of the entity or the property value in native language
def extractDescription(info):
    return info.get('descriptions', {}).get('en', {}).get('value', "")
    
def method1_infobox(wd, bio):
    result = {}
    #get entity from api
    entity_info = getEntityInfo(wd)
    result['name'] = translator.get_transliteration(extractName(entity_info))
    result['description'] = translator.get_translation(extractDescription(entity_info))
    #explicitly query using sparql to get main biography data
    for entity, wdt in bio.items():
        spqrqlq = f"SELECT ?entity ?entityLabel ?entityDescription WHERE {{ wd:{wd} wdt:{wdt} ?entity; SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"en\". }} }}"
        v = ""
        res = get_results(endpoint_url, str(spqrqlq))
        for entities in res['results']['bindings']:
            value = entities.get('entityLabel').get('value', "")
            if value != '' and 'Q' not in value:
                v += value + ','
        if v != "":
            if entity in to_transliteration:
                result[entity] = translator.get_transliteration(v)
            else:
                result[entity] = translator.get_translation(v)
    return result


# ### Method2

# In[ ]:


import wptools
import json
from tqdm import tqdm
import re
import requests as r
from collections import defaultdict


# In[ ]:


def update(infobox , translator):
    infobox = defaultdict(str , infobox)
    updated_infobox = {}
    updated_infobox['name'] = translator.get_transliteration(infobox['name'])
    updated_infobox['native_name'] = infobox['native_name']
    updated_infobox['category'] = translator.get_translation(infobox['settlement_type'])
    
    updated_infobox['image'] = infobox['image_skyline']
    if updated_infobox['image'] == '' : 
        updated_infobox['image'] = infobox['image']
    updated_infobox['image_caption'] = translator.get_translation(infobox['image_caption'])
    updated_infobox['flag'] = infobox['flag']
    updated_infobox['map'] = infobox['map']
    updated_infobox['map_caption'] = translator.get_translation(infobox['map_caption'])
    updated_infobox['motto'] = translator.get_transliteration(infobox['motto'])
    updated_infobox['timezone'] = infobox['timezone']
    
    updated_infobox['country'] = translator.get_translation(infobox['country'])
    updated_infobox['state'] = translator.get_translation(infobox['state'])
    updated_infobox['region'] = translator.get_translation(infobox['region'])
    updated_infobox['district'] = translator.get_translation(infobox['district'])
    updated_infobox['municipality'] = translator.get_translation(infobox['municipality'])
    updated_infobox['location'] = translator.get_translation(infobox['location'])
    updated_infobox['area'] = infobox['area_km2']
    updated_infobox['length'] = infobox['length_km']
    updated_infobox['width'] = infobox['width_km']
    
    updated_infobox['population'] = translator.get_translation(infobox['population'])
    updated_infobox['elevation'] = infobox['elevation_m']
    
    updated_infobox['animal'] = translator.get_translation(infobox['animal'])
    updated_infobox['plant'] = translator.get_translation(infobox['plant'])
    updated_infobox['geology'] = translator.get_translation(infobox['geology'])
    updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
    cur_len = len(updated_infobox)
    if len(updated_infobox) < 15:
        for key , val in infobox.items():
            if key in updated_infobox : continue
            updated_infobox[key] = translator.get_transliteration(val)
            if len(updated_infobox) == 15: break
    updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
    return updated_infobox


# In[ ]:


def method2_infobox(name):
    page = wptools.page(name).get_parse()
    result = update(page.data['infobox'] , translator)
    return result


# ### Baseline

# In[ ]:


def getEntityInfo(eid):
    return get_entity_dict_from_api(eid)

#extract the name of the entity or the property value in native language
def extractNameBaseline(info):
    return info.get('labels', {}).get('hi', {}).get('value', "")

#extract the description of the entity or the property value in native language
def extractDescriptionBaseline(info):
    return info.get('descriptions', {}).get('hi', {}).get('value', "")
    
def baseline_infobox(wd, bio):
    result = {}
    #get entity from api
    entity_info = getEntityInfo(wd)
    #print name and description
    result['name'] = extractNameBaseline(entity_info)
    result['description'] = extractDescriptionBaseline(entity_info)
    #explicitly query using sparql to get main biography data
    for entity, wdt in bio.items():
        spqrqlq = f"SELECT ?entity ?entityLabel ?entityDescription WHERE {{ wd:{wd} wdt:{wdt} ?entity; SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"hi\". }} }}"
        v = ""
        res = get_results(endpoint_url, str(spqrqlq))
        for entities in res['results']['bindings']:
            value = entities.get('entityLabel').get('value', "")
            if value != '' and 'Q' not in value:
                v += value + ','
        if v != "":
            result[entity] = v
    return result


# In[ ]:


with open('../data-collection/places/final_places.json') as f:
    data = json.loads(f.read())['data']
for ind , val in enumerate(data):
    val['index'] = ind


# In[ ]:


get_ipython().run_line_magic('timeit', '')
for entry in data[:1800]:
    try :
        print(entry['wd_id'] , entry['en_wikipedia_title'])
        method1 = method1_infobox(entry['wd_id'], properties)
        method2 = method2_infobox(entry['en_wikipedia_title'])
        baseline = baseline_infobox(entry['wd_id'],properties)
        output = {
            "method_1" : method1,
            "method_2" : method2,
            "baseline" : baseline
        }
        with open('places_till_1800.jsonl' , 'a+') as f:
            f.write(json.dumps({entry['index'] : output} , ensure_ascii = False))
            f.write("\n")
    except Exception as e:
        print(e)        

