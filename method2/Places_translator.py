import wptools
import json
from tqdm import tqdm
import re
import requests as r
from collections import defaultdict
try:
    from method2.Translator_Api import Translator_Api
except :
    from Translator_Api import Translator_Api
    
# Translator class for the places category
class Places_translator(Translator_Api):
    # https://docs.microsoft.com/en-us/azure/cognitive-services/translator/reference/v3-0-reference
    def __init__(self):
        self.api = Translator_Api()

    # Translate/Transliterate values
    def update(self , infobox):
        if infobox == None : 
            return {}
        infobox = defaultdict(str , infobox)
        updated_infobox = {}
        updated_infobox['name'] = self.api.get_transliteration(infobox['name'])
        updated_infobox['native_name'] = infobox['native_name']
        updated_infobox['category'] = self.api.get_translation(infobox['settlement_type'])

        updated_infobox['image'] = infobox['image_skyline']
        if updated_infobox['image'] == '' : 
            updated_infobox['image'] = infobox['image']
        updated_infobox['image_caption'] = self.api.get_translation(infobox['image_caption'])
        updated_infobox['flag'] = infobox['flag']
        updated_infobox['map'] = infobox['map']
        updated_infobox['map_caption'] = self.api.get_translation(infobox['map_caption'])
        updated_infobox['motto'] = self.api.get_transliteration(infobox['motto'])
        updated_infobox['timezone'] = infobox['timezone']

        updated_infobox['country'] = self.api.get_translation(infobox['country'])
        updated_infobox['state'] = self.api.get_translation(infobox['state'])
        updated_infobox['region'] = self.api.get_translation(infobox['region'])
        updated_infobox['district'] = self.api.get_translation(infobox['district'])
        updated_infobox['municipality'] = self.api.get_translation(infobox['municipality'])
        updated_infobox['location'] = self.api.get_translation(infobox['location'])
        updated_infobox['area'] = infobox['area_km2']
        updated_infobox['length'] = infobox['length_km']
        updated_infobox['width'] = infobox['width_km']


        updated_infobox['population'] = self.api.get_translation(infobox['population'])
        updated_infobox['elevation'] = infobox['elevation_m']

        updated_infobox['animal'] = self.api.get_translation(infobox['animal'])
        updated_infobox['plant'] = self.api.get_translation(infobox['plant'])
        updated_infobox['geology'] = self.api.get_translation(infobox['geology'])

        updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
        cur_len = len(updated_infobox)
        if len(updated_infobox) < 15:
            for key , val in infobox.items():
                if key in updated_infobox : continue
                updated_infobox[key] = self.api.get_transliteration(val)
                if len(updated_infobox) == 15: break
        updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
        return updated_infobox

    # Pretty print infobox
    def change_format(self,infobox):
        infobox = [ ("|" + key + " = " +  val) for key , val in infobox.items()]
        print("{{Geobox")
        print("\n".join(infobox))
        print("}}")
        
    # Get the page uisng wptools
    def get_page(self,page_name , language = "en"):
        return wptools.page(page_name , lang = language).get_parse()
        
    def get_infobox(self,page_name , test = False):
        page = self.get_page(page_name)
        new_infobox = self.update(page.data['infobox'])
        if not test:
            self.change_format(new_infobox)
        return new_infobox
        
if __name__ == "__main__":
    translator = Places_translator()
    infobox = translator.get_infobox("Amman")