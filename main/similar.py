import cv2
import os
from main.models import *
from main import db
from linebot.models.actions import MessageAction

def save_user(is_nomal_face,user_id,group_id,message_id):
    user = User(is_nomal_face,user_id,group_id,message_id,0)
    db.session.add(user)
    db.session.commit()

def save_inm_and_score(user_id,group_id,is_nomal_face,score):
    user = db.session.query(User).filter_by(group_id=group_id).filter_by(user_id=user_id).first()
    user.is_nomal_face = is_nomal_face
    user.score = score
    db.session.add(user)
    db.session.commit()


def save_inm_and_mid(user_id,message_id,group_id,is_nomal_face):
    user = db.session.query(User).filter_by(group_id=group_id).filter_by(user_id=user_id).first()
    user.is_nomal_face = is_nomal_face
    user.message_id = message_id
    db.session.add(user)
    db.session.commit()
    

def take_message_id(group_id,user_id):
    user = db.session.query(User).filter_by(group_id=group_id).filter_by(user_id=user_id).first()
    return user.message_id

def take_is_nomal_face(group_id,user_id):
    user = db.session.query(User).filter_by(group_id=group_id).filter_by(user_id=user_id).first()
    return user.is_nomal_face

def is_user_id(user_id):
    user = db.session.query(User).filter_by(user_id=user_id).all()
    if user == None:
        return False
    else:
        return True


def is_group_id(group_id):
    user = db.session.query(User).filter_by(group_id=group_id).all()
    if user == None:
        return False
    else:
        return True

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

    return int(score) #点数調整必須

def save_starting_game(game):
    sg = db.session.query(Startinggame).filter_by(id=1).first()
    sg.game = game
    db.session.add(sg)
    db.session.commit()

def take_starting_game():
    game = db.session.query(Startinggame).filter_by(id=1).first()
    return game.game
