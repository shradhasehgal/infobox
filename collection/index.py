import xml.sax
import sys , os , re , regex
import nltk
from datetime import datetime
import json
import pickle as pkl

# # Try using default dict 
# # Try differnet stop words
# # Try different stemmer

# Getting the Stop Words
from nltk.corpus import stopwords
from spacy.lang.en.stop_words import STOP_WORDS
stop_words = set(stopwords.words("english"))

# Defining the stemmer
from nltk.stem import SnowballStemmer , PorterStemmer 
from Stemmer import Stemmer
en_stemmer = SnowballStemmer('english')
porter_stemmer = PorterStemmer()
port_pystemmer = Stemmer('porter')
en_pystemmer = Stemmer('english')
stem_words = {}
# print(STOP_WORDS)
# print(type(STOP_WORDS))

words_dict = {}
title_dict = {}
total_num_tokens = 0

def process(token):
    token = token.lower()
    if token not in stem_words:
        stem_words[token] = port_pystemmer.stemWord(token) # Using PyStemmer Porter
        # stem_words[token] = en_pystemmer.stemWord(token) # Using PyStemmer English
        # stem_words[token] = porter_stemmer.stem(token) # Using NLTK Porter
        # stem_words[token] = en_stemmer.stem(token) # Using NLTK SnowBall
    token = stem_words[token]
    # if len(token) <= 1 or token in stop_words : return None # NLTK
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
        # return " ".join(regex.findall(r"(?=\{Infobox)(\{([^{}]|(?1))*\})", text[0]))
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
    def startElement(self,tag,attributes):
        self.tag = tag
        if self.tag == 'title': self.flag = 1

    def endElement(self,tag):
        if tag == "text":
    #        index(self.docID,self.title.strip(),self.data)
            self.docID+=1
            self.title = self.title.strip()
            # if "संभल" in self.title:
            #     print("YEet" , self.title.__repr__())
            if "{{Infobox" not in self.data and "{{ज्ञानसन्दूक" not in self.data:
                self.count+=1
                # field2[self.title.strip()].append(apply_regex(self.data,"c"))
                cat = apply_regex(self.data , "c")
                f = False
                
                for _cat in cat:
                    # if "लोग" in _cat.split(" "):
                    # if "लोग" in _cat:
                    #     f = True
                    # field2[_cat].append(self.id)

                    for x in _cat.split(" "):
                        field2[x].append(self.title)
                # if f:
                #     field2["लोग"]+=1
                #field2[self.title.strip()].append(clean(self.data , "c"))                
                #print(x.__repr__())
                #field2[x].append((self.title , self.data))
            self.data = ''
            self.title = ''
            self.id = ''
            self.redirect = False
        elif tag == 'id':
            self.flag = 0
        elif tag == "mediawiki":
            pass
        
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
print("time to parse is ", parse_end-begin)
print("Number of files with infobox is " ,Handler.count)
# print(field , len(field))

print("time to index is ",datetime.now() - parse_end)


# आन्ध्र प्रदेश 4580
# चित्र जोड़ें 3909
# जीवित लोग 3117
# बिहार के गाँव 1792
# गाँव 1751
# मेल एक्स्प्रेस ट्रेन 1516
# अदिलाबादु जिला 1454
# रायगढ़ जिला, छत्तीसगढ़ 1370
# वर्ष 1325
# पटना जिला के गाँव 1259


# के 60686
# तहसील 23484
# गाँव 17284
# में 14715
# जिला 14323
# लोग 12766
# उत्तराखण्ड 11012
# भारत 10510
# की 9532
# भारतीय 8883
# प्रदेश 7666
# का 6196
# हिन्दी 5791
# जन्मे 5767
# आन्ध्र 4781
# बिहार 4562
# चित्र 4038
# जोड़ें 3910
# इतिहास 3388
# देशानुसार 3165


# ['चकिया\n    ',
#  'कौसानी\n    ',
#  'कौसानी\n    ',
#  'अठपैसिया, कांडा तहसील\n    ',
#  'अठपैसिया, कांडा तहसील\n    ']





# चित्र जोड़ें 3283
# मेल एक्स्प्रेस ट्रेन 1515
# वर्ष 1325
# जीवित लोग 1100
# हिन्दी विकि डीवीडी परियोजना 935
# कार्बनिक यौगिक 821
# व्यक्तिगत जीवन 746
# नामानुसार भारत के ज़िले 705
# भागलपुर जिला के गाँव 609
# हिन्दी साहित्य 527
# हिन्दू धर्म 519
# मुंगेर जिला के गाँव 498
# अकार्बनिक यौगिक 490
# बिहार 488
# हिन्दी 458
# बिहार के प्रखण्ड 415
# गूगल परियोजना 371
# साहित्य 371
# शब्दार्थ 371
# संभल तहसील के गाँव 371

# भारत 8160
# भारतीय 4925
# लोग 4636
# गाँव 4170
# हिन्दी 3666
# चित्र 3403
# जोड़ें 3284
# ईसा 3001
# वर्ष|पूर्व, 2996
# जन्मे 2986
# देशानुसार 2612
# इतिहास 2508
# अनुसार 2170
# प्रदेश 2108
# विज्ञान 2031
# जिला 1986
