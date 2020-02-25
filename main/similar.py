#import cv2
from main.models import Imagemodel, Modelstatus
from main import db

def save_message_id(message_id):
    im = Imagemodel(message_id)
    db.session.add(im)
    db.session.commit()

def take_first_message_id():
    im = db.session.query(Imagemodel).all()
    return im[-1].message_id

def save_exist_model(exist_model):
    ms = Modelstatus(exist_model)
    db.session.add(ms)
    db.session.commit()

def take_first_exist_model():
    ms = db.session.query(Modelstatus).all()
    return ms[-1].exist_model

