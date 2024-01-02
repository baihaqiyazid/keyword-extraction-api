from flask_restx import fields

from .extension import api


keyword_input_model = api.model("KeywordInput", {
    "sentence": fields.String("Ini adalah contoh berita full teks dari artikel input."),
})

response_success = api.model('ResponseSuccess', {
    "code": fields.Integer(200),
    "status": fields.String("success"),
    "message": fields.String(""),
    "result": fields.List(
        fields.String,
        example=[
            "kepala desa cibodas dindin sukaya",
            "kolam renang vila bellevue",
            "kabupaten bandung barat"
        ]
    )
})

response_method_not_allowed = api.model('ResponseMethodNotAllowed', {
    "code": fields.Integer(405),
    "status": fields.String("NOK"),
    "message": fields.String("Method Not Found!"),
})

response_bad_request = api.model('ResponseBadRequest', {
    "code": fields.Integer(400),
    "status": fields.String("Bad Request"),
    "message": fields.String("No text provided"),
})

response_parameter_not_valid = api.model('ResponseParameterNotValid', {
    "code": fields.Integer(500),
    "status": fields.String("NOK"),
    "message": fields.String("parameter not valid"),
})

input_config_model = api.model('InputConfigModel', {
    "min_chars": fields.Integer(5),
    "max_words":fields.Integer(5),
    "min_freq":fields.Integer(1),
    "lang_detect_threshold":fields.Integer(10),
    "max_words_unknown_lang":fields.Integer(2),
    "generated_stopwords_percentile":fields.Integer(10),
    "generated_stopwords_max_len":fields.Integer(3),
    "generated_stopwords_min_freq":fields.Integer(1),
})

response_success_config = api.model('ResponseSuccessConfig', {
    "code": fields.Integer(200),
    "status": fields.String("success"),
    "message": fields.String("Changed"),
    "result": fields.Nested(api.model('ConfigParameterModelAPI', {
        "min_chars": fields.Integer(20),
        "max_words": fields.Integer(50),
        "min_freq": fields.Integer(1),
        "language_code":fields.String('id'),
        "stopwords": fields.String('stopwordsid2'),
        "lang_detect_threshold": fields.Integer(10),
        "max_words_unknown_lang": fields.Integer(3),
        "generated_stopwords_percentile": fields.Integer(10),
        "generated_stopwords_max_len": fields.Integer(3),
        "generated_stopwords_min_freq": fields.Integer(1)
    })),
})
