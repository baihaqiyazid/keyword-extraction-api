import re
from multi_rake import Rake
from app.data.helper.cleaning import stopwordsid2, prefinkb


# RAKE PARAMETER DEFAULT
min_chars=20,
max_words=50,
min_freq=1,
language_code='id',  # 'en'
stopwords=stopwordsid2,  # {'and', 'of'}
lang_detect_threshold=10,
max_words_unknown_lang=3,
generated_stopwords_percentile=10,
generated_stopwords_max_len=3,
generated_stopwords_min_freq=1

rake = Rake(
    min_chars=20,
    max_words=50,
    min_freq=1,
    language_code='id',  # 'en'
    stopwords=stopwordsid2,  # {'and', 'of'}
    lang_detect_threshold=10,
    max_words_unknown_lang=3,
    generated_stopwords_percentile=10,
    generated_stopwords_max_len=3,
    generated_stopwords_min_freq=1, )

## BEBAS
def sortKey(elem):
    return elem[1]

def rakeid(text):
    clean_text = prefinkb(text)
    keywords = rake.apply(clean_text)
    keywords.sort(key=sortKey, reverse=True)
    return [keyw[0] for keyw in keywords[0:10]]


