from method1.utils import getInfobox

biography = {
    
    "name": "P251",
    "image": "P18",
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

def method1_infobox(qid,category):
    return getInfobox(qid,properties if category == 'places' else biography)