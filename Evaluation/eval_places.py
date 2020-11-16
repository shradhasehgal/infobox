#!/usr/bin/env python
# coding: utf-8

# ### Method 1

# In[2]:


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
sys.path.append('../method2')
from People_translator import Translation_Api
translator = Translation_Api()


# In[3]:


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


# In[4]:


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

endpoint_url = "https://query.wikidata.org/sparql"


# In[5]:


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
        v =  ""
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

# In[6]:


import wptools
import json
from tqdm import tqdm
import re
import requests as r
from collections import defaultdict


# In[7]:


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


# In[8]:


def method2_infobox(name):
    page = wptools.page(name).get_parse()
    result = update(page.data['infobox'] , translator)
    return result


# ### Baseline

# In[9]:


def getEntityInfo(eid):
    return get_entity_dict_from_api(eid)

#extract the name of the entity or the property value in native language
def extractNameBaseline(info):
    return info.get('labels', {}).get('hi', {}).get('value', "")

#extract the description of the entity or the property value in native language
def extractDescriptionBaseline(info):
    return info.get('descriptions', {}).get('hi', {}).get('value', "")

#print the name and the description
def printNameAndDescriptionBaseline(info, trans):
    name = extractName(info)
    if name != "":
        print(trans['name'] + ":", name)
    desc = extractDescription(info)
    if desc != "":
        print(trans['description'] + ":", desc)
    
def baseline_infobox(wd, bio):
    result = {}
    #get entity from api
    entity_info = getEntityInfo(wd)
    #print name and description
#     printNameAndDescription(entity_info, trans)
    result['name'] = extractNameBaseline(entity_info)
    result['description'] = extractDescriptionBaseline(entity_info)
    #explicitly query using sparql to get main biography data
#     print("----------------------",trans['main_info'],"----------------------")
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
#             print(s + v)
            


# In[10]:


def get_score(translated_infobox , actual_infobox):
    inst = inexactsearch.InexactSearch()
    markings = defaultdict(list)
    for key in translated_infobox.keys():
        if key in actual_infobox.keys() and key!='image':
#             print(key)
#             print(translated_infobox[key] , actual_infobox[key]) 
            val = inst.compare(translated_infobox[key] , actual_infobox[key])
            if val > 0.70 :
                markings['C'].append(key)
            else : markings['S'].append(key)
    for key in actual_infobox.keys():
        if key not in translated_infobox.keys():
            markings['D'].append(key)
    if len(markings['C']) + len(markings['S']) != 0:
        precision = len(markings['C']) / (len(markings['C']) + len(markings['S']))
    else : precision = 0
    recall = len(markings['C']) / (len(markings['C']) + len(markings['S']) + len(markings['D']))
    print('Precisions :',precision)
    print('Recall :',recall)
    return precision , recall


# In[15]:


with open('../data-collection/places/eval_places.json') as f:
    data = json.loads(f.read())['data']
wiki_places = []
for entry in data:
    try :
        wiki_places.append([entry['en_wikipedia_title'] , entry['hi_wikipedia_title'] , entry['wd_id']])
    except :
        pass


# In[19]:


def parse_infobox(text):
    for key in  ["{{Infobox","{{ज्ञानसन्दूक","{{Geobox","{{ज्ञानसंदूक"]:
        if key in text :
            text =  text.split(key)[1]
            break
    else: 
        return None
    text = text.split("\n")[1:]
    ret = {}
    for line in text:
        if line == "}}" : break
        if line[0] != '|' : continue
        x,y = line[2:].split(" = ")
        ret[x] = y
    else :
        print("Parsing Error")
        assert(False)
    return ret


# In[23]:


final_score = []
for en_name , hi_name , qid in wiki_places[:1]:
    try:
        print(en_name , hi_name , qid)
        actual_infobox = parse_infobox(translator.get_page(hi_name , language = 'hi').data['wikitext'])
        if actual_infobox == None: continue
        method1 = method1_infobox(qid, properties)
        method2 = method2_infobox(en_name)
        baseline = baseline_infobox(qid,properties)
        final_score.append({en_name : [method1 , method2 , baseline , actual_infobox]})
        with open('places_eval.jsonl' , 'a+') as f:
            f.write(json.dumps(final_score[-1] , ensure_ascii = False))
            f.write("\n")
    except Exception as e:
        print(e)
        print(en_name)
print()


# In[29]:


import pickle as pkl
with open("final_places.pkl" , "wb") as f:
    pkl.dump(final_score , f)

