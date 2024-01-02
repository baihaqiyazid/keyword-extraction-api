from .extension import db

class Sentiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classified_text =  db.Column(db.String)
    tweet_text =  db.Column(db.String)
    sentence_score =  db.Column(db.String)
    max_positive =  db.Column(db.Integer)
    max_negative =  db.Column(db.Integer)
    kelas =  db.Column(db.String)