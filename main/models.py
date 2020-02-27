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
    

class Instruments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupid = db.Column(db.String(80))
    userid = db.Column(db.String(80))
    message = db.Column(db.String(100))
    status = db.Column(db.String(15))
    icon = db.Column(db.String(200))

    def __init__(self, groupid, userid, message, status, icon):
        self.groupid = groupid
        self.userid = userid
        self.message = message
        self.status = status
        self.icon = icon

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(80))

    def __init__(self, answer):
        self.answer = answer

def init():
    db.create_all()
        
