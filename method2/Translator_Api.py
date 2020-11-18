import requests as r
import json
import re
from collections import defaultdict

class Translator_Api():
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