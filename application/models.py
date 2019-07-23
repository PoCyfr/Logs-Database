from application import db

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(db.String(128), index=True, unique=False)
    
    def __init__(self, notes):
        self.notes = notes

    def __repr__(self):
        return '<Data %r>' % self.notes

class message(db.Model):
    f1 = db.Column(db.Float)
    f2 = db.Column(db.Integer)
    f3 = db.Column(db.Integer)
    f4 = db.Column(db.Integer)
    f5 = db.Column(db.Integer)
    f6 = db.Column(db.Integer)
    f7 = db.Column(db.Integer)
    f8 = db.Column(db.Integer)
    f9 = db.Column(db.Integer)
    f10 = db.Column(db.Integer)
    f11 = db.Column(db.Integer)
    f12 = db.Column(db.Integer)
    f13 = db.Column(db.Integer)
    f14 = db.Column(db.Integer)
    ID = db.Column(db.Integer,  primary_key=True)