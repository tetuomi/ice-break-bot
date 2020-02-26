from flask import request, abort
from main import app, line_bot_api, handler, db
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage, StickerSendMessage, AudioSendMessage, ImageMessage,TemplateSendMessage
)
from linebot.models.template import CarouselColumn,CarouselTemplate
from linebot.models.actions import MessageAction
import os
import random

from main.models import *
from main.similar import *

from pathlib import Path

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    save_starting_game(event.message.text)

    game = take_starting_game()

    group_id = event.source.group_id
    
    if game == "変顔":
        reply_message=TextSendMessage("画像を送ってね")
    elif game == "これ誰":
        reply_message=TextSendMessage("自己紹介を個チャでしてね") # おがしゅんよろ
    else:
        reply_message = TemplateSendMessage(
            "tempalte",
            CarouselTemplate(
                [
                    CarouselColumn(
                        thumbnail_image_url="https://ice-breake.herokuapp.com/static/yattinda.jpg",
                        title="変顔採点",
                        text=f"変顔を採点します\n普通の顔と変顔を送ってください\n\n１位 :{get_ranking({group_id})}",
                        actions=[MessageAction("遊ぶ", "変顔")]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://rr.img.naver.jp/mig?src=http%3A%2F%2Fimgcc.naver.jp%2Fkaze%2Fmission%2FUSER%2F20140722%2F51%2F5551361%2F4%2F480x602xbb1ca7f0feef63f896500253.jpg%2F300%2F600&twidth=300&theight=600&qlt=80&res_format=jpg&op=r",
                        title="これだーれだ？",
                        text="botに個人チャットで自己紹介文を送ってください\nおがしゅんあとで追加よろしく60文字以内",
                        actions=[MessageAction("遊ぶ", "これ誰")]
                    )
                ]
            )
        )
    
    if event.message.text == "やめる":
        save_starting_game("None")
        reply_message = TextSendMessage("ばいばーい")

    line_bot_api.reply_message(event.reply_token, reply_message)
        
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    game = take_starting_game()
    
    if game == "変顔":
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        group_id = event.source.group_id
        message_id = event.message.id

        message_content = line_bot_api.get_message_content(message_id)
        with open(Path(f"main/static/{message_id}.jpg").absolute(), "wb") as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        
        if is_user_id(user_id):
            if is_group_id(group_id):
                if take_is_nomal_face(group_id,user_id):
                    funny_face_path = "main/static/{}.jpg".format(message_id)
                    nomal_face_path = "main/static/{}.jpg".format(take_message_id(group_id,user_id))
                    score=score_funny_face(nomal_face_path,funny_face_path)
                    reply_message = TextSendMessage(f'「{profile.display_name}」さんは\n\n{score}点\n\nまた普通の顔を送ってね')
                    save_inm_and_score(user_id,group_id,False,score)
                    
                    Path(funny_face_path).unlink()
                    Path(nomal_face_path).unlink()

                else:
                    save_inm_and_mid(user_id,message_id,group_id,True)
                    reply_message = TextSendMessage(f'「{profile.display_name}」さんの普通の顔を確認しました')
            else:
                save_user(True,user_id,group_id,message_id)
                reply_message = TextSendMessage(f'「{profile.display_name}」さんの普通の顔を確認しました')
        else:
            save_user(True,user_id,group_id,message_id)
            reply_message = TextSendMessage(f'「{profile.display_name}」さんの普通の顔を確認しました')
        line_bot_api.reply_message(event.reply_token,reply_message)

    
