from main import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_nomal_face = db.Column(db.Boolean)
    user_id = db.Column(db.String(80))
    group_id = db.Column(db.String(80))
    message_id = db.Column(db.String(80))
    score = db.Column(db.Integer)
    def __init__(self,is_nomal_face,user_id,group_id,message_id,score):
        self.is_nomal_face = is_nomal_face
        self.user_id = user_id
        self.group_id = group_id
        self.message_id = message_id
        self.score = score

class Startinggame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.String(80))

    def __init__(self,game):
        self.game = game
    
def init():
    db.create_all()
        
