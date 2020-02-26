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
    
    if game == "変顔":
        message=TextSendMessage("画像を送ってね")
    elif game == "これ誰":
        message=TextSendMessage("自己紹介を個チャでしてね") # おがしゅんよろ
    else:
        message = TemplateSendMessage(
            "tempalte",
            CarouselTemplate(
                [
                    CarouselColumn(
                        thumbnail_image_url="https://ice-breake.herokuapp.com/static/yattinda.jpg",
                        title="変顔採点",
                        text="はじめに画像を送ってください\nその人がモデルとなります\nモデルに似た変顔を決め込んで、画像を送りましょう\n100点満点で採点されます\n「やめる」を入力すると、ゲームを終了します",
                        actions=MessageAction("遊ぶ", "変顔")
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://rr.img.naver.jp/mig?src=http%3A%2F%2Fimgcc.naver.jp%2Fkaze%2Fmission%2FUSER%2F20140722%2F51%2F5551361%2F4%2F480x602xbb1ca7f0feef63f896500253.jpg%2F300%2F600&twidth=300&theight=600&qlt=80&res_format=jpg&op=r",
                        title="これだーれだ？",
                        text="botに個人チャットで自己紹介文を送ってください\nおがしゅんあとで追加よろしく\n「やめる」を入力すると、ゲームを終了します",
                        actions=MessageAction("遊ぶ", "これ誰")
                    )
                ]
            )
        )
    
    if event.message.text == "やめる":
        save_exist_model(False)
        save_starting_game("None")
        message = TextSendMessage("ばいばーい")

    line_bot_api.reply_message(event.reply_token, message)
        
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    game = take_starting_game()
    
    if game == "変顔":
        profile = line_bot_api.get_profile(event.source.user_id)
        message_id = event.message.id
        
        message_content = line_bot_api.get_message_content(message_id)
        message_img_path = f"main/static/{message_id}.jpg"
        with open(Path(message_img_path).absolute(), "wb") as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
                
        if take_first_exist_model():
                    
            model_id = take_first_message_id()
            model_img_path = f"main/static/{model_id}.jpg"
                    
            score = score_funny_face(model_img_path, message_img_path)
        
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='「' + profile.display_name + f'」さんは\n\n{score}点(100)')
            )
        
            Path(message_img_path).absolute().unlink()
        
        else:
            save_exist_model(True)
            save_message_id(message_id)
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='「' + profile.display_name + '」さんの画像を\nモデルにしました')
            )

            
