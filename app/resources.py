from flask_restx import Resource, Namespace
import logging
from app.data.model.keybert622fix import keybertid, max_sum_sim, mmr
from app.data.model.yake import yake_, custom_kw_extractor, prefin2, yakeid
from app.data.model.rake622fix import prefinkb, rakeid, rake, sortKey, stopwordsid2
from .api_model import input_config_model, keyword_input_model, response_success, response_success_config, response_method_not_allowed, response_bad_request, response_parameter_not_valid
from .response import ResponseFormat
from werkzeug.exceptions import BadRequest, InternalServerError, MethodNotAllowed

ns = Namespace("ke/v1")

logging.basicConfig(format="[%(asctime)s] - [%(levelname)s] - [%(name)s] - %(message)s", filename="logging.log")
logging.getLogger('werkzeug').disabled = True
logging.getLogger('app').disabled = True

logger_route_yake = logging.getLogger("/ke/v1/yake")
logger_route_yake.setLevel(20)

logger_route_yake_config = logging.getLogger("/ke/v1/yake/config")
logger_route_yake_config.setLevel(20)

logger_route_mrake = logging.getLogger("/ke/v1/mrake")
logger_route_mrake.setLevel(20)

logger_route_mrake_config = logging.getLogger("/ke/v1/mrake/config")
logger_route_mrake_config.setLevel(20)

logger_route_keybert = logging.getLogger("/ke/v1/keybert")
logger_route_keybert.setLevel(20)

logger_route_keybert_config = logging.getLogger("/ke/v1/keybert/config")
logger_route_keybert_config.setLevel(20)

# RAKE PARAMETER DEFAULT
min_chars = 20
max_words = 50
min_freq = 1
language_code = 'id'  # 'en'
stopwords = stopwordsid2  # {'and', 'of'}
lang_detect_threshold = 10
max_words_unknown_lang = 3
generated_stopwords_percentile = 10
generated_stopwords_max_len = 3
generated_stopwords_min_freq = 1

# APPLY MODEL
def applyModel(text):
    rake.min_chars = min_chars
    rake.max_words = max_words
    rake.min_freq = min_freq
    rake.stopwords = stopwords
    rake.max_words_unknown_lang = max_words_unknown_lang
    rake.generated_stopwords_percentile = generated_stopwords_percentile
    rake.generated_stopwords_max_len = generated_stopwords_max_len
    rake.generated_stopwords_min_freq = generated_stopwords_min_freq
    rake.language_code = language_code

    clean_text = prefinkb(text)
    keywords = rake.apply(clean_text)
    keywords.sort(key=sortKey, reverse=True)
    return [keyw[0] for keyw in keywords[0:10]]

# YAKE PARAMETER DEFAULT
language = "id"
max_ngram_size = 3
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 5

def applyModelYake():
    custom_kw_extractor.n = max_ngram_size
    custom_kw_extractor.dedupLim = deduplication_thresold
    custom_kw_extractor.deduplication_algo = deduplication_algo
    custom_kw_extractor.windowsSize = windowSize
    custom_kw_extractor.top = numOfKeywords

    return custom_kw_extractor

# KEYBERT PARAMETER DEFAULT
n_gram_range = (1,3)
top_n = 3
algo = "normal"
nr_candidates = 20
diversity = 0.5


@ns.route("/keybert")
class SentimentAPIKeyBert(Resource):
    @ns.expect(keyword_input_model)
    @ns.response(200, 'Success', response_success)
    @ns.response(405, 'Method Not Allowed', response_method_not_allowed)
    @ns.response(400, 'Bad Request', response_bad_request)
    @ns.response(500, 'Parameter Not Valid', response_parameter_not_valid)
    def post(self):
        if "sentence" not in ns.payload:
            logger_route_mrake.error(f"ERROR: {InternalServerError.code}")
            raise InternalServerError("parameter not valid")
        
        
        if ns.payload["sentence"] == None or ns.payload["sentence"] == "":
            logger_route_mrake.error(f"ERROR: {BadRequest.code}")
            raise BadRequest("No text provided")
        
     
        if algo == "normal":
            output = keybertid(ns.payload["sentence"], n_gram_range, top_n)   
        elif algo == "max_sum_sim":  
            output = max_sum_sim(ns.payload["sentence"], n_gram_range, top_n, nr_candidates) 
        else:   
            output = mmr(ns.payload["sentence"], n_gram_range, top_n, diversity)     
        
        response = ResponseFormat(data=output, config=None, message="").to_dict()
        sentence = ns.payload["sentence"]

        if len(sentence) > 80:
            sentence = sentence[:80]

        logger_route_keybert.info(f"sentence: {sentence} - value: {response}")

        return response  
    
    def get(self):
        logger_route_keybert.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def put(self):
        logger_route_keybert.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def patch(self):
        logger_route_keybert.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def delete(self):
        logger_route_keybert.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def head(self):
        logger_route_keybert.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def options(self):
        logger_route_keybert.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed  

@ns.route("/keybert/config")  
class ConfigParameterModelAPIKeybert(Resource):
   
    def checkParameter(self, param, param_text):
        if param_text not in ns.payload:
           param = param
           return param
        
        elif ns.payload[param_text] == None or ns.payload[param_text] == "":
           logger_route_mrake_config.error(f"ERROR: {BadRequest.code}")
           raise BadRequest(f"{param_text} value cannot be null")
        
        else:
            if(param_text != "n_gram_range"):
               param = ns.payload[param_text]
               return param
            else:
               param = tuple(ns.payload[param_text])
               return param
    
    def checkParameterAlgo(self, param, param_text):
        if param_text not in ns.payload:
           param = param
           return param
        
        elif ns.payload[param_text] == None or ns.payload[param_text] == "":
           return "normal"
        
        else:
            if ns.payload[param_text] == "normal":
                param = ns.payload[param_text]
                return param

            elif ns.payload[param_text] == "max_sum_sim":
                param = ns.payload[param_text]
                return param
            
            elif ns.payload[param_text] == "mmr":
                param = ns.payload[param_text]
                return param

            else:
                raise BadRequest(f"algo only normal, max_sum_sim, mmr")
               
    @ns.expect(input_config_model)
    @ns.response(200, 'Success', response_success_config)
    @ns.response(405, 'Method Not Allowed', response_method_not_allowed)
    @ns.response(400, 'Bad Request', response_bad_request)
    @ns.response(500, 'Parameter Not Valid', response_parameter_not_valid)
    def post(self):
        global n_gram_range, top_n, algo, nr_candidates, diversity

        if not ns.payload:
            if algo == "normal":
                response = ResponseFormat(data=None, config={
                            "n_gram_range" :list(n_gram_range), 
                            "top_n" :top_n,
                            "algo" : algo
                        }, message="").to_dict()
                
                logger_route_keybert_config.info(f"n_gram_range: {n_gram_range}, top_n: {top_n}, algo: {algo}")
                
            elif algo == "max_sum_sim":
                response = ResponseFormat(data=None, config={
                            "n_gram_range" :list(n_gram_range), 
                            "top_n" :top_n,
                            "algo" : algo,
                            "nr_candidates" : nr_candidates
                        }, message="").to_dict()
                logger_route_keybert_config.info(f"n_gram_range: {n_gram_range}, top_n: {top_n}, algo: {algo}, nr_candidates: {nr_candidates}")
                
            else:
                response = ResponseFormat(data=None, config={
                            "n_gram_range" :list(n_gram_range), 
                            "top_n" :top_n,
                            "algo" : algo,
                            "diversity" : diversity
                        }, message="").to_dict()
                logger_route_keybert_config.info(f"n_gram_range: {n_gram_range}, top_n: {top_n}, algo: {algo}, diversity: {diversity}")
        
            return response   
        
        else:
            n_gram_range = self.checkParameter(n_gram_range, "n_gram_range")
            top_n = self.checkParameter(top_n, "top_n")
            nr_candidates = self.checkParameter(nr_candidates, "nr_candidates")
            diversity = self.checkParameter(diversity, "diversity")
            algo = self.checkParameterAlgo(algo, "algo")

            if algo == "normal": 
                response = ResponseFormat(data={
                    "n_gram_range" :list(n_gram_range), 
                    "top_n" :top_n,
                    "algo": algo
                }, config=None, message="Changed").to_dict()
                logger_route_keybert_config.info(f"n_gram_range: {n_gram_range}, top_n: {top_n}, algo: {algo}")
                
            elif algo == "max_sum_sim": 
                response = ResponseFormat(data={
                    "n_gram_range" :list(n_gram_range), 
                    "top_n" :top_n,
                    "algo": algo,
                    "nr_candidates" : nr_candidates
                }, config=None, message="Changed").to_dict()
                logger_route_keybert_config.info(f"n_gram_range: {n_gram_range}, top_n: {top_n}, algo: {algo}, nr_candidates: {nr_candidates}")

            else:
                response = ResponseFormat(data={
                    "n_gram_range" :list(n_gram_range), 
                    "top_n" :top_n,
                    "algo": algo,
                    "diversity" : diversity
                }, config=None, message="Changed").to_dict()
                logger_route_keybert_config.info(f"n_gram_range: {n_gram_range}, top_n: {top_n}, algo: {algo}, diversity: {diversity}")
           
            return response

    def get(self):
        logger_route_keybert_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def put(self):
        logger_route_keybert_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def patch(self):
        logger_route_keybert_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def delete(self):
        logger_route_keybert_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def head(self):
        logger_route_keybert_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def options(self):
        logger_route_keybert_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed     

@ns.route("/mrake")
class SentimentAPI(Resource):
    @ns.expect(keyword_input_model)
    @ns.response(200, 'Success', response_success)
    @ns.response(405, 'Method Not Allowed', response_method_not_allowed)
    @ns.response(400, 'Bad Request', response_bad_request)
    @ns.response(500, 'Parameter Not Valid', response_parameter_not_valid)
    def post(self):
        if "sentence" not in ns.payload:
            logger_route_mrake.error(f"ERROR: {InternalServerError.code}")
            raise InternalServerError("parameter not valid")
        
        
        if ns.payload["sentence"] == None or ns.payload["sentence"] == "":
            logger_route_mrake.error(f"ERROR: {BadRequest.code}")
            raise BadRequest("No text provided")

        output = applyModel(ns.payload["sentence"])     
        response = ResponseFormat(data=output, config=None, message="").to_dict()
        
        sentence = ns.payload["sentence"]
        
        if len(sentence) > 80:
            sentence = sentence[:80]

        logger_route_mrake.info(f"sentence: {sentence} - value: {response}")

        return response  
    
    def get(self):
        logger_route_mrake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def put(self):
        logger_route_mrake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def patch(self):
        logger_route_mrake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def delete(self):
        logger_route_mrake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def head(self):
        logger_route_mrake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def options(self):
        logger_route_mrake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed  

@ns.route("/mrake/config")  
class ConfigParameterModelAPI(Resource):
   
    def checkParameter(self, param, param_text):
        if param_text not in ns.payload:
           param = param
           return param
        
        elif ns.payload[param_text] == None or ns.payload[param_text] == "":
           logger_route_mrake_config.error(f"ERROR: {BadRequest.code}")
           raise BadRequest(f"{param_text} value cannot be null")
        
        else:
           param = ns.payload[param_text]
           return param

    @ns.expect(input_config_model)
    @ns.response(200, 'Success', response_success_config)
    @ns.response(405, 'Method Not Allowed', response_method_not_allowed)
    @ns.response(400, 'Bad Request', response_bad_request)
    @ns.response(500, 'Parameter Not Valid', response_parameter_not_valid)
    def post(self):
        global min_chars, max_words, min_freq, language_code, stopwords, lang_detect_threshold, max_words_unknown_lang, generated_stopwords_percentile, generated_stopwords_max_len, generated_stopwords_min_freq

        if not ns.payload:
            response = ResponseFormat(data=None, config={
                        "min_chars" :min_chars, 
                        "max_words" :max_words,
                        "min_freq" :min_freq,
                        "language_code": language_code,  # 'en'
                        "stopwords" : "stopwordsid2",  # {'and', 'of'}
                        "lang_detect_threshold" : lang_detect_threshold,
                        "max_words_unknown_lang" : max_words_unknown_lang,
                        "generated_stopwords_percentile" : generated_stopwords_percentile,
                        "generated_stopwords_max_len" : generated_stopwords_max_len,
                        "generated_stopwords_min_freq" : generated_stopwords_min_freq
                    }, message="").to_dict()
            
            logger_route_mrake_config.info(f"min_chars: {min_chars}, max_words: {max_words}, min_freq: {min_freq}, language_code: {language_code}, lang_detect_threshold: {lang_detect_threshold}, max_words_unknown_lang: {max_words_unknown_lang}, generated_stopwords_percentile: {generated_stopwords_percentile}, generated_stopwords_max_len: {generated_stopwords_max_len}, generated_stopwords_min_freq: {generated_stopwords_min_freq}")
            return response   
        
        else:
            min_chars = self.checkParameter(min_chars, "min_chars")
            max_words = self.checkParameter(max_words, "max_words")
            min_freq = self.checkParameter(min_freq, "min_freq")
            lang_detect_threshold = self.checkParameter(lang_detect_threshold, "lang_detect_threshold")
            max_words_unknown_lang = self.checkParameter(max_words_unknown_lang, "max_words_unknown_lang")
            generated_stopwords_percentile = self.checkParameter(generated_stopwords_percentile, "generated_stopwords_percentile")
            generated_stopwords_max_len = self.checkParameter(generated_stopwords_max_len, "generated_stopwords_max_len")
            generated_stopwords_min_freq = self.checkParameter(generated_stopwords_min_freq, "generated_stopwords_min_freq")

            response = ResponseFormat(data={
                "min_chars" :min_chars, 
                "max_words" :max_words,
                "min_freq" :min_freq,
                "language_code": language_code,  # 'en'
                "stopwords" : "stopwordsid2",  # {'and', 'of'}
                "lang_detect_threshold" : lang_detect_threshold,
                "max_words_unknown_lang" : max_words_unknown_lang,
                "generated_stopwords_percentile" : generated_stopwords_percentile,
                "generated_stopwords_max_len" : generated_stopwords_max_len,
                "generated_stopwords_min_freq" : generated_stopwords_min_freq
            }, config=None, message="Changed").to_dict()

            logger_route_mrake_config.info(f"min_chars: {min_chars}, max_words: {max_words}, min_freq: {min_freq}, language_code: {language_code}, lang_detect_threshold: {lang_detect_threshold}, max_words_unknown_lang: {max_words_unknown_lang}, generated_stopwords_percentile: {generated_stopwords_percentile}, generated_stopwords_max_len: {generated_stopwords_max_len}, generated_stopwords_min_freq: {generated_stopwords_min_freq}")
            return response

    def get(self):
        logger_route_mrake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def put(self):
        logger_route_mrake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def patch(self):
        logger_route_mrake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def delete(self):
        logger_route_mrake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def head(self):
        logger_route_mrake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def options(self):
        logger_route_mrake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed     

@ns.route("/yake")
class SentimentAPI(Resource):
    @ns.expect(keyword_input_model)
    @ns.response(200, 'Success', response_success)
    @ns.response(405, 'Method Not Allowed', response_method_not_allowed)
    @ns.response(400, 'Bad Request', response_bad_request)
    @ns.response(500, 'Parameter Not Valid', response_parameter_not_valid)
    def post(self):
        if "sentence" not in ns.payload:
            logger_route_yake.error(f"ERROR: {InternalServerError.code}")
            raise InternalServerError("parameter not valid")
        
        if ns.payload["sentence"] == None or ns.payload["sentence"] == "":
            logger_route_yake.error(f"ERROR: {BadRequest.code}")
            raise BadRequest("No text provided")
        
        extractor = applyModelYake()
        output = yakeid(ns.payload["sentence"], extractor)     
        response = ResponseFormat(data=output, config=None, message="").to_dict()

        sentence = ns.payload["sentence"]
        
        if len(sentence) > 80:
            sentence = sentence[:80]

        logger_route_yake.info(f"sentence: {sentence}")

        return response
    
    def get(self):
        logger_route_yake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def put(self):
        logger_route_yake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def patch(self):
        logger_route_yake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def delete(self):
        logger_route_yake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def head(self):
        logger_route_yake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def options(self):
        logger_route_yake.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed

@ns.route("/yake/config")          
class ConfigParameterModelAPI(Resource):

    def checkParameter(self, param, param_text):
        if param_text not in ns.payload:
           param = param
           return param
        
        elif ns.payload[param_text] == None or ns.payload[param_text] == "":
           logger_route_yake_config.error(f"ERROR: {BadRequest.code}")
           raise BadRequest(f"{param_text} value cannot be null")
        
        else:
           param = ns.payload[param_text]
           return param

    @ns.expect(input_config_model)
    @ns.response(200, 'Success', response_success_config)
    @ns.response(405, 'Method Not Allowed', response_method_not_allowed)
    @ns.response(400, 'Bad Request', response_bad_request)
    @ns.response(500, 'Parameter Not Valid', response_parameter_not_valid)
    def post(self):
        global language, max_ngram_size, deduplication_thresold, deduplication_algo, windowSize, numOfKeywords
        
        if not ns.payload:
            response = ResponseFormat(data=None, config={
                        "language" :language, 
                        "max_ngram_size" :max_ngram_size,
                        "deduplication_thresold" :deduplication_thresold,
                        "deduplication_algo": deduplication_algo,
                        "windowSize" : windowSize,
                        "numOfKeywords" : numOfKeywords
                    }, message="").to_dict()
            logger_route_yake_config.info(f"language: {language}, max_ngram_size: {max_ngram_size}, deduplication_thresold: {deduplication_thresold}, windowSize: {windowSize}, numOfKeywords: {numOfKeywords}")
            return response   
    
        else:
            max_ngram_size = self.checkParameter(max_ngram_size, "max_ngram_size")
            deduplication_thresold = self.checkParameter(deduplication_thresold, "deduplication_thresold")
            deduplication_algo = self.checkParameter(deduplication_algo, "deduplication_algo")
            numOfKeywords = self.checkParameter(numOfKeywords, "numOfKeywords")
            windowSize = self.checkParameter(windowSize, "windowSize")
        
            response = ResponseFormat(data={
                    "language" :language, 
                    "max_ngram_size" :max_ngram_size,
                    "deduplication_thresold" :deduplication_thresold,
                    "deduplication_algo": deduplication_algo,
                    "windowSize" : windowSize,
                    "numOfKeywords" : numOfKeywords
            }, config=None, message="Changed").to_dict()
            logger_route_yake_config.info(f"language: {language}, max_ngram_size: {max_ngram_size}, deduplication_thresold: {deduplication_thresold}, windowSize: {windowSize}, numOfKeywords: {numOfKeywords}")
            return response   
        
    def get(self):
        logger_route_yake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def put(self):
        logger_route_yake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def patch(self):
        logger_route_yake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def delete(self):
        logger_route_yake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def head(self):
        logger_route_yake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
    
    def options(self):
        logger_route_yake_config.error(f"ERROR: {MethodNotAllowed.code}")
        raise MethodNotAllowed
       
