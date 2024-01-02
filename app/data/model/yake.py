#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 13:29:53 2022

@author: putri
"""

from app.data.helper.cleaning import stopwordsid2, cleaning, normalizing
import nltk
import yake
import re
from nltk import word_tokenize, sent_tokenize
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

factoryStopword = StopWordRemoverFactory()
stopword = factoryStopword.create_stop_word_remover()
stop_factory = StopWordRemoverFactory().get_stop_words()

# Merge stopword
data = set(stop_factory + stopwordsid2)
#remove stopword
def removeStopword(str):
    word_tokens = word_tokenize(str)
    filtered_sentence = [w for w in word_tokens if not w in data]
    return ' '.join(filtered_sentence)

def tokkal(str):
    str = nltk.tokenize.sent_tokenize(str)
    return str

"""
#stemming non aktif
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


factoryStemmer = StemmerFactory()
stemmer = factoryStemmer.create_stemmer()

def stemming(text):
  return stemmer.stem(text)

def stringdulu(text):
    return str(text)

"""
def presatu(str):
    str = cleaning(str)
    str = normalizing(str)
    str = tokkal(str)
    return str

def predua(strr):
  strr = str(strr)
  #strr = stemming(strr)
  strr = removeStopword(strr)
  return strr

def sppra(text):
    text = re.split(r"\n+", text)
    return text

def norml(text):
    text_jadi = ''
    for paragraf in text :
        paragraf_presatu = presatu(paragraf)
        paragraf_jadi = ''
        for kalimat in paragraf_presatu:
            kalimatdua = predua(kalimat) + '. '
            paragraf_jadi = paragraf_jadi + kalimatdua
            #return paragraf_jadi
        text_jadi = text_jadi + '\n\n' + paragraf_jadi
    return text_jadi

def prefin2(datatext):
    datatext1 = sppra(datatext)
    datatext2 = norml(datatext1)
    return datatext2

language = "id"
max_ngram_size = 3
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 5

custom_kw_extractor = yake.KeywordExtractor(lan=language,
                                            n=max_ngram_size,
                                            dedupLim=deduplication_thresold,
                                            dedupFunc=deduplication_algo,
                                            windowsSize=windowSize,
                                            top=numOfKeywords, features=None)


def sortKey(elem):
    return elem[1]

def yake_(text, extractor):
    # print(extractor.n)
    # print(extractor.deduplication_algo)
    # print(extractor.top)
    keywords = extractor.extract_keywords(text)
    keywords.sort(key=sortKey, reverse=True)
    return [keyw[0] for keyw in keywords[0:extractor.top]]

def yakeid(text, extractor):
    clean_text = prefin2(text)
    keywords = yake_(clean_text, extractor)
    return keywords
    
