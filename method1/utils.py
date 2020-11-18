import sys
from qwikidata.sparql import return_sparql_query_results
from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api
from SPARQLWrapper import SPARQLWrapper, JSON

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

endpoint_url = "https://query.wikidata.org/sparql"

# calls qwikidata get entity function for an entity id
def getEntityInfo(eid):
    return get_entity_dict_from_api(eid)

# Extract the name of the entity or the property value in native language
def extractName(info):
    return info.get('labels', {}).get('hi', {}).get('value', "")

# Extract the description of the entity or the property value in native language
def extractDescription(info):
    return info.get('descriptions', {}).get('hi', {}).get('value', "")

# Print the name and the description
def printNameAndDescription(info):
    return extractName(info)
    
def getInfobox(wd, bio):
    # Get entity from api
    entity_info = getEntityInfo(wd)
    # Print name and description
    result = {}
    result['name'] = printNameAndDescription(entity_info)
    # Explicitly query using sparql to get main biography data
    # print("----------------------",trans['main_info'],"----------------------")
    for entity, wdt in bio.items():
        spqrqlq = f"SELECT ?entity ?entityLabel ?entityDescription WHERE {{ wd:{wd} wdt:{wdt} ?entity; SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"hi\". }} }}"
        v = ""
        res = get_results(endpoint_url, str(spqrqlq))
        for entities in res['results']['bindings']:
            value = entities.get('entityLabel').get('value', "")
            if value != '' and 'Q' not in value:
                v = value
        if v != "":
            result[entity] = v
    return result