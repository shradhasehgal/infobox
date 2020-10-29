from utils import getInfobox

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

translation = {}
getInfobox('Q1353', properties, translation)

# property_dict = {
#     "name": P2561 ,
#     "native_name": P1559 / P1705 ,
#     "category / settlement_type": type of location, can be a type of protected area, settlement type etc.,/
#         if left blank the first parameter with which the Geobox is called is used (i.e. River, Valley, Settlement etc.),
    
#     "image" , P18
#     "image_caption": P2096 ( might work ) ,
    
#     "flag": P163,
#     "map": P242,
#     "map_caption": ,
#     "motto":P1546,
#     "timezone": P2907,
    
#     "country": P17,
#     "state": state(s), in which the location lies, use | state_type= to change displayed from "State" to another e.g. "Province", "County",
#     "region": region(s) in which the location lies,
#     "district": district(s) which the location lies,
#     "municipality": municiplity/municipalities in which the location lies,
    
#     "location": P276,
#     "area / area_km2": P2046,
#     "length / length_km": P2043,
#     "width / width_km": P2049,
    
#     "population": P1082,
#     "elevation / elevation_m":P2044 ,
#     "animal" : major animals living in the area,
#     "plant" : major plants growing in the area,
#     "geology" : P2695,
    
# }