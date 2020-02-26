import cv2
import os
from main.models import Imagemodel, Modelstatus, Startinggame
from main import db
from linebot.models.actions import MessageAction

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

def score_funny_face(model_img_path, compare_img_path):
    IMG_SIZE = (200, 200)
    
    model_img = cv2.imread(model_img_path, cv2.IMREAD_GRAYSCALE)
    model_img = cv2.resize(model_img, IMG_SIZE)

    compare_img = cv2.imread(compare_img_path, cv2.IMREAD_GRAYSCALE)
    compare_img = cv2.resize(compare_img, IMG_SIZE)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)

    detector = cv2.AKAZE_create()
    (model_kp, model_des) = detector.detectAndCompute(model_img, None)
    (compare_kp, compare_des) = detector.detectAndCompute(compare_img, None)

    matches = bf.match(model_des, compare_des)
    dist = [m.distance for m in matches]

    score = sum(dist) / len(dist)

    return score #点数調整必須

def save_starting_game(game):
    sg = db.session.query(Startinggame).filter_by(id=1).first()
    sg.game = game
    db.session.add(sg)
    db.session.commit()

def take_starting_game():
    game = db.session.query(Startinggame).filter_by(id=1).first()
    return game.game
