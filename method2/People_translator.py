import wptools
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
    
    def update(self,infobox , translator):
        infobox = defaultdict(str , infobox)
        updated_infobox = {}
        updated_infobox['name'] = translator.get_transliteration(infobox['name'])

        updated_infobox['image'] = infobox['image']

        updated_infobox['caption'] = translator.get_translation(infobox['caption'])

        updated_infobox['fullname'] = translator.get_transliteration(infobox['fullname'])
        updated_infobox['nickname'] = translator.get_transliteration(infobox['nickname'])

        infobox['birth_date'] = infobox['birth_date'].replace("df|","df").replace("|yes","yes")
        updated_infobox['residence'] = translator.get_transliteration(infobox['residence'])
        updated_infobox['birth_date'] = translator.get_translation(infobox['birth_date'])
        updated_infobox['birth_place'] = translator.get_translation(infobox['birth_place'])

        updated_infobox['death_date'] = translator.get_translation(infobox['death_date'])
        updated_infobox['death_place'] = translator.get_transliteration(infobox['death_place'])

        updated_infobox['country'] = translator.get_translation(infobox['country'])
        updated_infobox['nationality'] = translator.get_translation(infobox['nationality'])
        updated_infobox['occupation'] = translator.get_translation(infobox['occupation'])
        updated_infobox['profession'] = translator.get_translation(infobox['profession'])
        updated_infobox['positions'] = translator.get_translation(infobox['positions'])
        updated_infobox['heightm'] = infobox['heightm']
        updated_infobox['gender'] = translator.get_translation(infobox['gender'])

        updated_infobox['spouse'] = translator.get_transliteration(infobox['spouse'])
        updated_infobox['children'] = translator.get_transliteration(infobox['children'])
        updated_infobox['parents'] = translator.get_transliteration(infobox['parents'])
        updated_infobox['father'] = translator.get_transliteration(infobox['father'])
        updated_infobox['mother'] = translator.get_transliteration(infobox['mother'])

        updated_infobox['party'] = translator.get_translation(infobox['party'])
        updated_infobox['awards'] = translator.get_transliteration(infobox['awards'])
        updated_infobox['relations'] = translator.get_translation(infobox['relations'])
        updated_infobox['known_for'] = translator.get_translation(infobox['known_for'])
        updated_infobox['notable_works'] = translator.get_transliteration(infobox['notable_works'])

        updated_infobox['alma_mater'] = translator.get_translation(infobox['alma_mater'])
        updated_infobox['education'] = translator.get_translation(infobox['education'])
        updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
        cur_len = len(updated_infobox)
        if len(updated_infobox) < 15:
            for key , val in infobox.items():
                if key in updated_infobox : continue
                updated_infobox[key] = translator.get_transliteration(val)
                if len(updated_infobox) == 15: break
        updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
        return updated_infobox


    def change_format(self,infobox):
        infobox = [ ("|" + key + " = " +  val) for key , val in infobox.items()]
        print("{{Infobox person")
        print("\n".join(infobox))
        print("}}")
        
    def get_page(self,page_name , language = "en"):
        return wptools.page(page_name , lang = language).get_parse()
        
    def get_infobox(self,page_name , test = False):
        print(self , page_name)
        page = self.get_page(page_name)
        translator = Translation_Api()
        new_infobox = self.update(page.data['infobox'] , translator)
        if not test:
            self.change_format(new_infobox)
        return new_infobox
        
if __name__ == "__main__":
    translator = Translation_Api()
    data = "Sample Text"
    print("Translation for {} is {}".format(data , translator.get_translation(data)))
    data = "Sample Text"
    print("Transliteration for {} is {}".format(data , translator.get_transliteration(data)))
