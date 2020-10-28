from utils import getInfobox

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

translation = {
    "name":"नाम",
    "description":"विवरण",
    "image": "चित्र",
    "gender":"लिंग",
    "residence":"निवास",
    "place_of_birth":"जन्म स्थान",
    "date_of_birth":"जन्मतारीख",
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

getInfobox('Q555240', biography, translation)