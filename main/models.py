from main import db

class Imagemodel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(80), unique=True)

    def __init__(self, message_id):
        self.message_id = message_id

class Modelstatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exist_model = db.Column(db.Boolean)

    def __init__(self, exist_model):
        self.exist_model = exist_model

    
def init():
    db.create_all()
        
