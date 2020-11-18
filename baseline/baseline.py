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
sys.path.append("..")
from method2.Translator_Api import Translator_Api
translator = Translator_Api()
from method1.utils import *

# Wikidata property IDs
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

# Fields which will be transliterated , rest will be translated
people_to_transliteration = ['name','birth_place','spouse','notable_works']
places_to_transliteration = ['name','motto']

# Function to get baseline infobox
def baseline_infobox(wd, category = 'people' , bio = biography, fields = people_to_transliteration):
    if category == 'places' :
        fields = places_to_transliteration
        bio = properties
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
            if entity in fields:
                result[entity] = translator.get_transliteration(v)
            else:
                result[entity] = translator.get_translation(v)
    return result

if __name__ == "__main__":
    # Information about Shane Warne
    baseline_infobox('Q555240', biography)

    # Information about New Delhi
    baseline_infobox("Q987", category='places')





