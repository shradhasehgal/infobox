#!/usr/bin/env python
# coding: utf-8

# In[231]:


import wptools
import json
from tqdm import tqdm
import re
import requests as r
from collections import defaultdict


# In[249]:


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
        if data == "" : return data
        data = [{"Text":data}]
        res = r.post( self.translate_url , json = data , headers = self.headers).text
        res = json.loads(res)
        res = [ ret['translations'][0]['text'] for ret in res ]
        return res[0].replace("[[","[").replace("]]","]").replace("[","[[").replace("]","]]")
        
    def get_transliteration(self,data):
        if data == "" : return data
        data = [{"Text":data}]
        res = r.post( self.transliterate_url , json = data , headers = self.headers).text
        res = json.loads(res)
        res = [ret['text'] for ret in res]
        return res[0].replace("[[","[").replace("]]","]").replace("[","[[").replace("]","]]")


# In[250]:


translator = Translation_Api()


# In[251]:


data = "Sample Text"
translator.get_translation(data)


# In[252]:


data = "Sample Text"
translator.get_transliteration(data)


# In[253]:


page = wptools.page('Surdas').get_parse()


# In[259]:


def update(infobox , translator):
    infobox = defaultdict(str , infobox)
    updated_infobox = {}
    updated_infobox['name'] = translator.get_transliteration(infobox['name'])
    
    updated_infobox['image'] = infobox['image']
    
    updated_infobox['caption'] = translator.get_translation(infobox['caption'])
    
    updated_infobox['fullname'] = translator.get_transliteration(infobox['fullname'])
    updated_infobox['nickname'] = translator.get_transliteration(infobox['nickname'])
    
    infobox['birth_date'] = infobox['birth_date'].replace("df|","df").replace("|yes","yes")
    updated_infobox['birth_date'] = infobox['birth_date'] if "{{" in infobox['birth_date'] else translator.get_translation(infobox['birth_date'])
    updated_infobox['birth_place'] = translator.get_transliteration(infobox['birth_place'])
    
    updated_infobox['death_date'] = infobox['death_date'] if "{{" in infobox['death_date'] else translator.get_translation(infobox['death_date'])
    updated_infobox['death_place'] = translator.get_transliteration(infobox['death_place'])
    
    updated_infobox['country'] = translator.get_transliteration(infobox['country'])
    updated_infobox['occupation'] = translator.get_translation(infobox['occupation'])
    updated_infobox['heightm'] = infobox['heightm']
    
    updated_infobox['spouse'] = translator.get_transliteration(infobox['spouse'])
    updated_infobox['children'] = translator.get_transliteration(infobox['children'])
    updated_infobox['parents'] = translator.get_transliteration(infobox['parents'])
    updated_infobox['father'] = translator.get_transliteration(infobox['father'])
    updated_infobox['mother'] = translator.get_transliteration(infobox['mother'])
    
    updated_infobox['party'] = translator.get_translation(infobox['party'])
    updated_infobox['awards'] = translator.get_transliteration(infobox['awards'])
    updated_infobox['relations'] = translator.get_translation(infobox['relations'])
    updated_infobox['known_for'] = translator.get_translation(infobox['known_for'])
    
    updated_infobox['alma_mater'] = translator.get_translation(infobox['alma_mater'])
    updated_infobox = { key : val for key , val in updated_infobox.items() if val!=''}
    cur_len = len(updated_infobox)
    if len(updated_infobox) < 10:
        for key , val in infobox.items():
            if key in updated_infobox : continue
            updated_infobox[key] = translator.get_transliteration(val)
            if len(updated_infobox) == 10: break
    return updated_infobox


# In[260]:


new_infobox = update(page.data['infobox'] , translator)


# In[262]:


def change_format(infobox):
    infobox = [ ("|" + key + " = " +  val) for key , val in infobox.items()]
    print("{{Infobox person")
    print("\n".join(infobox))
    print("}}")


# In[263]:


new_infobox_string = change_format(new_infobox)


# In[ ]:




