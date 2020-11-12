#!/usr/bin/env python
# coding: utf-8

# ### Method 1

# In[10]:


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


# In[11]:


biography = {
    "image": "P18",
    "gender":"P21",
    "residence":"P551",
    "birth_place":"P19",
    "birth_date":"P569",
    "profession": "P106",
    "notable_works": "P800",
    "education": "P69",
    "positions":"P39",
    "awards": "P166",
    "spouse": "P26",
    "nationality": "P27",
}

translation = {
    "name":"नाम",
    "description":"विवरण",
    "image": "चित्र",
    "gender":"लिंग",
    "residence":"निवास",
    "birth_place":"जन्म स्थान",
    "birth_date":"जन्मतारीख",
    "profession": "व्यवसाय",
    "notable_works": "उल्लेखनीय कार्य",
    "education": "शिक्षा",
    "positions": "पद",
    "awards": "पुरस्कार",
    "spouse": "पति या पत्नी",
    "other_available_information":"अन्य उपलब्ध जानकारी",
    "main_info": "मुख्य जानकारी",
    "nationality": "राष्ट्रीयता"
}

to_transliteration = ['name','birth_place','spouse','notable_works']


# In[12]:


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

endpoint_url = "https://query.wikidata.org/sparql"


# In[13]:


#calls qwikidata get entity function for an entity id
def getEntityInfo(eid):
    return get_entity_dict_from_api(eid)

#extract the name of the entity or the property value in native language
def extractName(info):
    return info.get('labels', {}).get('en', {}).get('value', "")

#extract the description of the entity or the property value in native language
def extractDescription(info):
    return info.get('descriptions', {}).get('en', {}).get('value', "")
    
def method1_infobox(wd, bio, trans):
    result = {}
    #get entity from api
    entity_info = getEntityInfo(wd)
    result['name'] = translator.get_transliteration(extractName(entity_info))
    result['description'] = translator.get_translation(extractDescription(entity_info))
    #explicitly query using sparql to get main biography data
    for entity, wdt in bio.items():
        spqrqlq = f"SELECT ?entity ?entityLabel ?entityDescription WHERE {{ wd:{wd} wdt:{wdt} ?entity; SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"en\". }} }}"
        s, v = trans[entity] + ": ", ""
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

# In[14]:


import wptools
import json
from tqdm import tqdm
import re
import requests as r
from collections import defaultdict


# In[15]:


def update(infobox , translator):
    infobox = defaultdict(str , infobox)
    updated_infobox = {}
    updated_infobox['name'] = translator.get_transliteration(infobox['name'])
    
    updated_infobox['image'] = infobox['image']
    
    updated_infobox['caption'] = translator.get_translation(infobox['caption'])
    
    updated_infobox['fullname'] = translator.get_transliteration(infobox['fullname'])
    updated_infobox['nickname'] = translator.get_transliteration(infobox['nickname'])
    
    infobox['birth_date'] = infobox['birth_date'].replace("df|","df").replace("|yes","yes")
    updated_infobox['residence'] = translator.get_transliteration(infobox['residence'])
    updated_infobox['birth_date'] = translator.get_translation(infobox['birth_date'])
    updated_infobox['birth_place'] = translator.get_transliteration(infobox['birth_place'])
    
    updated_infobox['death_date'] = translator.get_translation(infobox['death_date'])
    updated_infobox['death_place'] = translator.get_transliteration(infobox['death_place'])
    
    updated_infobox['country'] = translator.get_transliteration(infobox['country'])
    updated_infobox['nationality'] = translator.get_translation(infobox['nationality'])
    updated_infobox['occupation'] = translator.get_translation(infobox['occupation'])
    updated_infobox['profession'] = translator.get_translation(infobox['profession'])
    updated_infobox['positions'] = translator.get_translation(infobox['positions'])
    updated_infobox['heightm'] = infobox['heightm']
    updated_infobox['gender'] = translator.get_translation(infobox['gender'])
    
    updated_infobox['spouse'] = translator.get_transliteration(infobox['spouse'])
    updated_infobox['children'] = translator.get_transliteration(infobox['children'])
    updated_infobox['parents'] = translator.get_transliteration(infobox['parents'])
    updated_infobox['father'] = translator.get_transliteration(infobox['father'])
    updated_infobox['mother'] = translator.get_transliteration(infobox['mother'])
    
    updated_infobox['party'] = translator.get_translation(infobox['party'])
    updated_infobox['awards'] = translator.get_transliteration(infobox['awards'])
    updated_infobox['relations'] = translator.get_translation(infobox['relations'])
    updated_infobox['known_for'] = translator.get_translation(infobox['known_for'])
    updated_infobox['notable_works'] = translator.get_transliteration(infobox['notable_works'])
    
    updated_infobox['alma_mater'] = translator.get_translation(infobox['alma_mater'])
    updated_infobox['education'] = translator.get_translation(infobox['education'])
    updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
    cur_len = len(updated_infobox)
    if len(updated_infobox) < 15:
        for key , val in infobox.items():
            if key in updated_infobox : continue
            updated_infobox[key] = translator.get_transliteration(val)
            if len(updated_infobox) == 15: break
    updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
    return updated_infobox


# In[16]:


def method2_infobox(name):
    page = wptools.page(name).get_parse()
    result = update(page.data['infobox'] , translator)
    return result


# ### Baseline

# In[24]:


def getEntityInfo(eid):
    return get_entity_dict_from_api(eid)

#extract the name of the entity or the property value in native language
def extractNameBaseline(info):
    return info.get('labels', {}).get('hi', {}).get('value', "")

#extract the description of the entity or the property value in native language
def extractDescriptionBaseline(info):
    return info.get('descriptions', {}).get('hi', {}).get('value', "")
    
def baseline_infobox(wd, bio, trans):
    result = {}
    #get entity from api
    entity_info = getEntityInfo(wd)
    #print name and description
    result['name'] = extractNameBaseline(entity_info)
    result['description'] = extractDescriptionBaseline(entity_info)
    #explicitly query using sparql to get main biography data
    for entity, wdt in bio.items():
        spqrqlq = f"SELECT ?entity ?entityLabel ?entityDescription WHERE {{ wd:{wd} wdt:{wdt} ?entity; SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"hi\". }} }}"
        s, v = trans[entity] + ": ", ""
        res = get_results(endpoint_url, str(spqrqlq))
        for entities in res['results']['bindings']:
            value = entities.get('entityLabel').get('value', "")
            if value != '' and 'Q' not in value:
                v += value + ','
        if v != "":
            result[entity] = v
    return result

with open('../data-collection/persons/primary_dataset_new_withlinks.json') as f:
    data = json.loads(f.read())
for ind , val in enumerate(data):
    val['index'] = ind


get_ipython().run_line_magic('timeit', '')
for entry in data[:1000]:
    try :
        print(entry['wd_id'] , entry['en_wikipedia_title'])
        method1 = method1_infobox(entry['wd_id'], biography,translation)
        method2 = method2_infobox(entry['en_wikipedia_title'])
        baseline = baseline_infobox(entry['wd_id'],biography,translation)
        output = {
            "method_1" : method1,
            "method_2" : method2,
            "baseline" : baseline
        }
        with open('people_output.jsonl' , 'a+') as f:
            f.write(json.dumps({entry['index'] : output} , ensure_ascii = False))
            f.write("\n")
    except Exception as e:
        print(e)