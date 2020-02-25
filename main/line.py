from flask import request, abort
from main import app, line_bot_api, handler, db
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage, StickerSendMessage, AudioSendMessage, ImageMessage
)
import os
import random

from main.models import Imagemodel, Modelstatus
from main.similar import (
    save_message_id, take_first_message_id, take_first_exist_model, save_exist_model, score_funny_face
)

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
    message = event.message.text

    if message == "やめる":
        save_exist_model(False)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))
    
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    message_id = event.message.id
    print(message_id)
    message_content = line_bot_api.get_message_content(message_id)
    message_img_path = f"main/static/{message_id}.jpg"
    with open(Path(message_img_path).absolute(), "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    
    if take_first_exist_model():

        model_id = take_first_message_id()
        model_img_path = f"main/static/{model_id}.jpg"

        print(model_id)
        
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

            
