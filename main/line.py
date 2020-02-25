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
    save_message_id, take_first_message_id, take_first_exist_model, save_exist_model
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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    if take_first_exist_model():
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=take_first_message_id())
        )
        save_exist_model(False)
        
    else:
        message_id = event.message.id
        save_exist_model(True)
        save_message_id(message_id)
        
        message_content = line_bot_api.get_message_content(message_id)
        file_path = f"main/static/{message_id}.jpg"
        with open(Path(file_path).absolute(), "wb") as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
            
        profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='「' + profile.display_name + '」さんの画像を\nモデルにしました')
        )

            
