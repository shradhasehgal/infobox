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
def printNameAndDescription(info, trans):
    name = extractName(info)
    if name != "":
        print(trans['name'] + ":", name)
    desc = extractDescription(info)
    if desc != "":
        print(trans['description'] + ":", desc)
        
# Print the information present in the entity itself
def printOtherInfo(entity, bio):
    # Get the claims subdict
    for p in entity['claims'].keys():
        if p not in bio.values():
            # Get information on the property in Hindi
            ent_info = getEntityInfo(p)
            name, desc = extractName(ent_info), extractDescription(ent_info)
            if name == "":
                continue # if the Hindi property name is not null
            value = ""
            
            # For every property in the claims subdict get information on the correspoding values
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
            # Print the property name and value only if the value is present in native language
            if value != "":
                print(name + ": " + value)
    
def getInfobox(wd, bio, trans):
    # Get entity from api
    entity_info = getEntityInfo(wd)
    # Print name and description
    printNameAndDescription(entity_info, trans)
    # Explicitly query using sparql to get main biography data
    print("----------------------",trans['main_info'],"----------------------")
    for entity, wdt in bio.items():
        spqrqlq = f"SELECT ?entity ?entityLabel ?entityDescription WHERE {{ wd:{wd} wdt:{wdt} ?entity; SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"hi\". }} }}"
        s, v = trans[entity] + ": ", ""
        res = get_results(endpoint_url,str(spqrqlq))
        for entity in res['results']['bindings']:
            value = entity.get('entityLabel').get('value', "")
            if value != '' and 'Q' not in value:
                v += value
        if v != "":
            print(s + v)
    # Print other relevant information if present in the entity 
    print("----------------------",trans['other_available_information'],"----------------------")
    printOtherInfo(entity_info, bio)
