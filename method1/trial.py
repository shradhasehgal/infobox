from qwikidata.sparql import return_sparql_query_results
from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api

biography = {
    "gender":"P21",
    "residence":"P551",
    "place_of_birth":"P19",
    "date_of_birth":"P569",
    "profession": "P106",
    "notable_works": "P800",
    "education": "P69",
    "positions":"P39",
    "awards": "P166",
    "spouse": "P26",
}

translation = {
    "name":"नाम",
    "description":"विवरण",
    "gender":"लिंग",
    "residence":"निवास",
    "place_of_birth":"जन्म स्थान",
    "date_of_birth":"जन्म की तारीख",
    "profession": "व्यवसाय",
    "notable_works": "उल्लेखनीय कार्य",
    "education": "शिक्षा",
    "positions": "पद",
    "awards": "पुरस्कार",
    "spouse": "पति या पत्नी",
    "other_available_information":"अन्य उपलब्ध जानकारी",
    "main_info": "मुख्य जानकारी",
}

#calls qwikidata get entity function for an entity id
def getEntityInfo(eid):
    return get_entity_dict_from_api(eid)

#extract the name of the entity or the property value in native language
def extractName(info):
    return info.get('labels', {}).get('hi', {}).get('value', "")

#extract the description of the entity or the property value in native language
def extractDescription(info):
    return info.get('descriptions', {}).get('hi', {}).get('value', "")

#print the name and the description
def printNameAndDescription(info, trans):
    name = extractName(info)
    if name != "":
        print(trans['name'] + ":", name)
    desc = extractDescription(info)
    if desc != "":
        print(trans['description'] + ":", desc)
        
#print the information present in the entity itself
def printOtherInfo(entity, bio):
    #get the claims subdict
#     print(entity['claims'])
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
                    value += pname + ","
            #only print property name and value if the value is present in native language
            if value != "":
                print(name + ": " + value)
    
def getBiography(wd, bio, trans):
    #get entity from api
    entity_info = getEntityInfo(wd)
    #print name and description
    printNameAndDescription(entity_info, trans)
    #explicitly query using sparql to get main biography data
    print("----------------------",trans['main_info'],"----------------------")
    for entity, wdt in bio.items():
        spqrqlq = f"SELECT ?entity ?entityLabel ?entityDescription WHERE {{ wd:{wd} wdt:{wdt} ?entity; SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"hi\". }} }}"
        s, v = trans[entity] + ": ", ""
        res = return_sparql_query_results(str(spqrqlq))
        for entity in res['results']['bindings']:
            value = entity.get('entityLabel').get('value', "")
            if value != '' and 'Q' not in value:
                v += value + ","
        if v != "":
            print(s + v)
    #euqry and print the rest of the data already present in the entity 
    print("----------------------",trans['other_available_information'],"----------------------")
    printOtherInfo(entity_info, bio)

#information about japanese game designer Hideo Kojima
getBiography('Q315577', biography, translation)
#information about  Narendra modi from the godfather
getBiography('Q1058', biography, translation)