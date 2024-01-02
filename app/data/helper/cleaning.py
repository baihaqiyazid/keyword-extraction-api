import re, sys
import pandas as pd

sys.path.append('.')
normalisasi = pd.read_csv('app/data/dbcor/kamusnorm.csv', encoding = 'latin-1')
normalisasi_map = dict(zip(normalisasi['original'], normalisasi['replacement']))

stopwordsid = pd.read_csv('app/data/dbcor/stopwords_id', header = None, names= ['stopword'])
stopwordsid2 = stopwordsid['stopword'].tolist()

#cleaning dataset
def cleaning(str):
    #Remove additional white spaces
    str = re.sub('[\s]+', ' ', str)
    #remove URLs
    str = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', str)
    #remove digit or numbers
    str = re.sub(r"\b\d+\b", " ", str)
    return str

def normalizing(text):
  return ' '.join([normalisasi_map[word] if word in normalisasi_map else word for word in text.split(' ')])

def presatu(str):
    str = cleaning(str)
    str = normalizing(str)
    return str

#memecah naskah menjadi per paragraf
def sppra(text):
    text = re.split(r"\n+", text)
    return text 

def norml(text):
    text_jadi = ''
    for paragraf in text :
        paragraf_presatu = presatu(paragraf)
        text_jadi = text_jadi + '\n\n' + paragraf_presatu
    return text_jadi

def prefinkb(datatext):
    datatext1 = sppra(datatext)
    datatext2 = norml(datatext1)
    return datatext2