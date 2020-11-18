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
    
# Translator class for the people category
class People_translator(Translator_Api):
    # https://docs.microsoft.com/en-us/azure/cognitive-services/translator/reference/v3-0-reference
    def __init__(self):
        self.api = Translator_Api()
        
    # Translate/Transliterate values
    def update(self,infobox):
        if infobox == None:
            return {}
        infobox = defaultdict(str , infobox)
        updated_infobox = {}
        updated_infobox['name'] = self.api.get_transliteration(infobox['name'])

        updated_infobox['image'] = infobox['image']

        updated_infobox['caption'] = self.api.get_translation(infobox['caption'])

        updated_infobox['fullname'] = self.api.get_transliteration(infobox['fullname'])
        updated_infobox['nickname'] = self.api.get_transliteration(infobox['nickname'])

        infobox['birth_date'] = infobox['birth_date'].replace("df|","df").replace("|yes","yes")
        updated_infobox['residence'] = self.api.get_transliteration(infobox['residence'])
        updated_infobox['birth_date'] = self.api.get_translation(infobox['birth_date'])
        updated_infobox['birth_place'] = self.api.get_translation(infobox['birth_place'])

        updated_infobox['death_date'] = self.api.get_translation(infobox['death_date'])
        updated_infobox['death_place'] = self.api.get_transliteration(infobox['death_place'])

        updated_infobox['country'] = self.api.get_translation(infobox['country'])
        updated_infobox['nationality'] = self.api.get_translation(infobox['nationality'])
        updated_infobox['occupation'] = self.api.get_translation(infobox['occupation'])
        updated_infobox['profession'] = self.api.get_translation(infobox['profession'])
        updated_infobox['positions'] = self.api.get_translation(infobox['positions'])
        updated_infobox['heightm'] = infobox['heightm']
        updated_infobox['gender'] = self.api.get_translation(infobox['gender'])

        updated_infobox['spouse'] = self.api.get_transliteration(infobox['spouse'])
        updated_infobox['children'] = self.api.get_transliteration(infobox['children'])
        updated_infobox['parents'] = self.api.get_transliteration(infobox['parents'])
        updated_infobox['father'] = self.api.get_transliteration(infobox['father'])
        updated_infobox['mother'] = self.api.get_transliteration(infobox['mother'])

        updated_infobox['party'] = self.api.get_translation(infobox['party'])
        updated_infobox['awards'] = self.api.get_transliteration(infobox['awards'])
        updated_infobox['relations'] = self.api.get_translation(infobox['relations'])
        updated_infobox['known_for'] = self.api.get_translation(infobox['known_for'])
        updated_infobox['notable_works'] = self.api.get_transliteration(infobox['notable_works'])

        updated_infobox['alma_mater'] = self.api.get_translation(infobox['alma_mater'])
        updated_infobox['education'] = self.api.get_translation(infobox['education'])
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
        print("{{Infobox person")
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
    translator = People_translator()
    infobox = translator.get_infobox("Virat Kohli")