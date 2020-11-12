
import sys
from qwikidata.sparql import return_sparql_query_results
from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api
from SPARQLWrapper import SPARQLWrapper, JSON
import json
from tqdm import tqdm
import re
import requests as r
from collections import defaultdict

class Translation_Api():
    # https://docs.microsoft.com/en-us/azure/cognitive-services/translator/reference/v3-0-reference
    def __init__(self):
        self.headers = {
                "Ocp-Apim-Subscription-Key":"e669322a133044489e6dc4e9cde3edee",
                "Content-Type":"application/json",
                "Ocp-Apim-Subscription-Region":"centralus"
            }
        self.transliterate_url = "https://api.cognitive.microsofttranslator.com/transliterate?api-version=3.0&language=hi&fromScript=Latn&toScript=Deva"
        self.translate_url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=hi&from=en&toScript=Deva"
    
    def get_translation(self,data):
        if "{{" in data : return data
        data = data.split("<ref>")[0]
        if data == "" : return data
        data = [{"Text":data}]
        res = r.post( self.translate_url , json = data , headers = self.headers).text
        res = json.loads(res)
        res = [ ret['translations'][0]['text'] for ret in res ]
        return res[0].replace("[[","[").replace("]]","]").replace("[","[[").replace("]","]]")
        
    def get_transliteration(self,data):
        if "{{" in data : return data
        data = data.split("<ref>")[0]
        if data == "" : return data
        data = [{"Text":data}]
        res = r.post( self.transliterate_url , json = data , headers = self.headers).text
        res = json.loads(res)
        res = [ret['text'] for ret in res]
        return res[0].replace("[[","[").replace("]]","]").replace("[","[[").replace("]","]]")
translator = Translation_Api()


# ### Program

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

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

endpoint_url = "https://query.wikidata.org/sparql"

#calls qwikidata get entity function for an entity id
def getEntityInfo(eid):
    return get_entity_dict_from_api(eid)

#extract the name of the entity or the property value in native language
def extractName(info):
    return info.get('labels', {}).get('en', {}).get('value', "")

#extract the description of the entity or the property value in native language
def extractDescription(info):
    return info.get('descriptions', {}).get('en', {}).get('value', "")

#print the name and the description
def printNameAndDescription(info, trans):
    name = extractName(info)
    if name != "":
        print(trans['name'] + ":", translator.get_transliteration(name))
    desc = extractDescription(info)
    if desc != "":
        print(trans['description'] + ":", translator.get_translation(desc))
        
#print the information present in the entity itself
def printOtherInfo(entity, bio):
    #get the claims subdict
    for p in entity['claims'].keys():
        if p not in bio.values():
            #get information on the property in bengali
            ent_info = getEntityInfo(p)
            name, desc = extractName(ent_info), extractDescription(ent_info)
            if name == "":
                continue
            value = ""
            #for every property in the claims subdict get inforamtion on the correspoding values
            for data in entity.get('claims', {}).get(p, []):
                res = data.get('mainsnak',{}).get('datavalue', {}).get('value', {})
                if type(res) == dict:
                    info_id = res.get('id', "")
                    if info_id == "":
                        continue
                    info = getEntityInfo(info_id)
                    pname, pdesc = extractName(info), extractDescription(info)
                    if pname == "":
                        continue
                    if pdesc != "":
                        pname += str(f'({pdesc})')
                    value += pname 
            #only print property name and value if the value is present in native language
            if value != "":
                print(name + ": " + value)
    
def getInfobox(wd, bio, trans):
    #get entity from api
    entity_info = getEntityInfo(wd)
    #print name and description
    printNameAndDescription(entity_info, trans)
    #explicitly query using sparql to get main biography data
    print("----------------------",trans['main_info'],"----------------------")
    for entity, wdt in bio.items():
        spqrqlq = f"SELECT ?entity ?entityLabel ?entityDescription WHERE {{ wd:{wd} wdt:{wdt} ?entity; SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"en\". }} }}"
        s, v = trans[entity] + ": ", ""
        res = get_results(endpoint_url, str(spqrqlq))
        for entity in res['results']['bindings']:
            value = entity.get('entityLabel').get('value', "")
            if value != '' and 'Q' not in value:
                v += value + ','
        if v != "":
            if entity in to_transliteration:
                v = translator.get_transliteration(v)
            else:
                v = translator.get_translation(v)
            print(s + v)

# Information about Shane Warne
getInfobox('Q555240', biography, translation)


# In[31]:

# Information about Narendra Modi
getInfobox('Q1058', biography, translation)


