import xml.sax
import sys , os , re , regex
import nltk
from datetime import datetime
import json
import pickle as pkl
import requests
from requests import utils
import ast

from nltk.corpus import stopwords
from spacy.lang.en.stop_words import STOP_WORDS
stop_words = set(stopwords.words("english"))

requests.packages.urllib3.disable_warnings()
from nltk.stem import SnowballStemmer , PorterStemmer 
from Stemmer import Stemmer
en_stemmer = SnowballStemmer('english')
porter_stemmer = PorterStemmer()
port_pystemmer = Stemmer('porter')
en_pystemmer = Stemmer('english')
stem_words = {}
words_dict = {}
title_dict = {}
total_num_tokens = 0

hindi_places_data = {}
with open('places_dataset_3.json') as f:
    infot = json.load(f)
    mapping = { info['hi_wikipedia_title'] : ind for ind , info in enumerate(infot['data'])}
    for info in infot['data']:
        hindi_places_data[info['hi_wikipedia_title']] = info['wd_id']

overall = {"data": []}
count = 0
def process(token):
    token = token.lower()
    if token not in stem_words:
        stem_words[token] = port_pystemmer.stemWord(token) # Using PyStemmer Porter
    token = stem_words[token]
    if len(token) <= 1 or token in STOP_WORDS or bool(re.match(r"[0-9]+[a-z]+[0-9a-z]*",token)) : return None # Spacy Faster 

    if token not in words_dict:
        words_dict[token] = ""
    return token

def apply_regex(text,field):
    if field == "i":
        text = text.split("{{Infobox")
        if len(text) == 1 : return ""
        ret = ""
        for line in text[1].split("\n"):
            if line == "}}" : break
            ret += line
        return ret
    if field == "c":
        text = text.split("[[श्रेणी:")[1:]
        ret = []
        for i in text:
            i = i.strip()
            if len(i) == 0 or (']]' not in i) : 
                # print("\n"*2 , i , i.__repr__()) 
                # sys.exit(0)
                break
            ret.append(i.split("]]")[0].strip().split("|")[0].strip())
        return ret            
        # return re.findall(r"\[\[श्रेणी:(.*)\]\]",text)
    if field == "r":
        return " ".join(re.findall("\{\{cite(.*?)\}\}<", text, flags=re.DOTALL))
    if field == "l":
        text = text.split("==External links==")
        if len(text) > 1:
            text = text[1].split("\n")
            ret = ""
            for line in text:
                if line and line[0] == "*" and len(line) > 1:
                    ret+=line[1:] + " "
            return ret

def clean(text , field):
    ''' To index complete document  / inside body '''
    if field not in ["b","t"]:
        text = apply_regex(text,field)
    ret = {}
    if not text : return 0,ret

    tokens = re.split(r'[^A-Za-z0-9]+',text)
    global total_num_tokens
    for token in tokens:
        token = process(token)
        if token == None : continue
        total_num_tokens+=1
        if token in ret:
            ret[token]+=1
        else : 
            ret[token] = 1
    return len(tokens),ret

def remove_refs(text):
    text = re.sub("<ref(.*?)>", "", text, flags=re.DOTALL)
    text = re.sub("/ref>", "", text)
    text = re.sub("\{\{cite(.*?)\}\}<", "", text, flags=re.DOTALL)
    return text


def index(docID,title,text):
    ''' helper function to deal with all cases '''
    doc_dict = {}
    num_tokens , doc_dict['b'] = clean(text,"b")
    _,doc_dict['t'] = clean(title,"t")
    _,doc_dict['r'] = clean(text,"r")
    text = remove_refs(text)
    _,doc_dict['c'] = clean(text,"c")
    _,doc_dict['i'] = clean(text,"i")
    _,doc_dict['l'] = clean(text,"l")
    temp = Document(docID,title,doc_dict)
    title_dict[docID] = title + " " + str(num_tokens) 
    
def get_wikidata_id_from_hindi(name):
    url = 'https://hi.wikipedia.org/w/api.php?action=query&prop=pageprops&titles='+name+'&format=json'
    try:
        response = requests.get(url)
        response_dict = ast.literal_eval(response.content.decode('utf-8'))
        for k,v in response_dict['query']['pages'].items():
            f = 0
            if 'wikibase_item' in v['pageprops']:
                return v['pageprops']['wikibase_item']
    except:
        return None

def get_english_from_wikidata(wikidata_id):
    # print(wikidata_id)
    url = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks&ids='+wikidata_id+'&sitefilter=enwiki'
    try:
        response = requests.get(url)
        response_dict = ast.literal_eval(response.content.decode('utf-8'))
        sitelinks = response_dict['entities'][wikidata_id]['sitelinks']
        if 'enwiki' in sitelinks:
            return sitelinks['enwiki']['title']
    except:
        return None

class Document():
    def __init__(self,docID,title,doc_dict):
        self.docID = docID
        self.title = title
        self.doc_dict = doc_dict
        self.to_index()

    def to_index(self):
        doc_dict_updated = {}
        for key in self.doc_dict:
            for token in self.doc_dict[key]:
                if token not in doc_dict_updated:
                    doc_dict_updated[token] = "d" + str(self.docID)
                doc_dict_updated[token] += key + str(self.doc_dict[key][token])
        for token in doc_dict_updated:
            words_dict[token]+=doc_dict_updated[token]
from collections import defaultdict

field2 = defaultdict(list)

class WikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.data = ''
        self.docID = 1
        self.title = ''
        self.tag = ''
        self.id = ''
        self.count = 0
        self.flag = 1
        self.redirect_val = ''
        self.redirect = False
    def startElement(self,tag,attributes):
        self.tag = tag
        if self.tag == 'title': self.flag = 1
        if self.tag == 'redirect':
            self.redirect_val = attributes._attrs['title'].strip()

    def endElement(self,tag):
        global count
        if tag == "text":
            self.docID+=1
            self.title = self.title.strip()
            if count  == 800:
                with open('eval_places.json','w+') as f:
                    json.dump(overall, f)
                exit(0)
            if "{{Infobox" in self.data or "{{ज्ञानसन्दूक" in self.data or "{{Geobox" in self.data or "{{ज्ञानसंदूक" not in self.data:
                self.count+=1
                cat = apply_regex(self.data , "c")
                f = False
            
                # if self.title in hindi_places_data or (('गाँव' in self.title or 'जिला' in self.title or self.title.endswith('नगर') or self.title.endswith('क्षेत्र')) and 'श्रेणी' not in self.title and 'साँचा' not in self.title):
                if self.title in hindi_places_data:
                    
                    info_dict = {"hi_wikipedia_title": self.title}
                    wiidata_id = None
                    if self.title not in hindi_places_data:
                        wikidata_id = get_wikidata_id_from_hindi(self.title)
                        if wikidata_id != 0:
                            info_dict['wd_id'] = wikidata_id
                    else:
                        wikidata_id = hindi_places_data[self.title] 
                        info_dict['wd_id'] = wikidata_id 
                    
                    if wikidata_id:
                        english_page = get_english_from_wikidata(wikidata_id)
                        # print(english_page)
                        if english_page:
                            info_dict['en_wikipedia_title'] = english_page
                            count += 1
                            overall['data'].append(info_dict)
                            # print(info_dict)
                            print(count)
                            print("\n")
                
            self.data = ''
            self.title = ''
            self.id = ''
            self.redirect = False
            self.redirect_val = ''
            
        elif tag == 'id':
            self.flag = 0
        elif tag == "mediawiki":
            pass
        elif tag == 'redirect':
            self.redirect = True
        
    def characters(self,content):
        if self.tag == "title":
            self.title+=content
        elif self.tag == "text":
            self.data+=content
        elif self.tag == 'id' and self.flag:
            self.id+=content


# Parsing code
file_path = sys.argv[1]
parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
Handler = WikiHandler()
parser.setContentHandler( Handler )
begin = datetime.now()
parser.parse(file_path)
parse_end = datetime.now()
print("Time to parse is ", parse_end-begin)
print("Number of files with infobox is " ,Handler.count)
print("time to index is ",datetime.now() - parse_end)
print("FINAL COUNT")
print(count)


with open('eval_places.json','w+') as f:
    json.dump(overall, f)
# json.dump(overall, fw)