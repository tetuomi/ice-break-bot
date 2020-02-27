from flask import request, abort
from main import app, line_bot_api, handler, db
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, FollowEvent, UnfollowEvent, JoinEvent, PostbackEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage, StickerSendMessage, AudioSendMessage, TemplateSendMessage,
    ConfirmTemplate, PostbackAction, MessageAction, QuickReplyButton, QuickReply
)
from linebot.models.template import CarouselColumn,CarouselTemplate
import os
import random

from main.models import *
from main.funny_face import *

from pathlib import Path
from sqlalchemy import func



def dealmessage(event):

    usermessage = event.message.text
    user_id = event.source.user_id
    messagetype = event.source.type

    if messagetype == "user":

        if db.session.query(Instruments).filter(Instruments.userid == user_id).first() == None:
            instruments = Instruments(None ,user_id ,None ,None ,None)
            db.session.add(instruments)
            db.session.commit()

        instruments = db.session.query(Instruments).filter(Instruments.userid == user_id).first()
        
        if instruments.status == "registing":
            instruments.message = usermessage
            instruments.status == "registed"
            db.session.add(instruments)
            db.session.commit()
            
            message = TemplateSendMessage(
            alt_text='Confirm Template',
            template=ConfirmTemplate(
                text="自己紹介は\n" + usermessage + "\nでいいですか？",
                actions=[
                    PostbackAction(
                        label="もう一回登録する",
                        display_text="もう一回登録する",
                        data="retry"
                    ),
                    PostbackAction(
                        label="これでいいよ",
                        display_text="これでいいよ",
                        data="ok"
                    )
                ]
            )
        )

        if usermessage == "自己紹介":
            message = TextSendMessage(text="次に送るメッセージを自己紹介に登録するね")
            
            instruments.status = "registing"
            db.session.add(instruments)
            db.session.commit()

        elif usermessage == "自分の自己紹介":
            my_instrument = db.session.query(Instruments).filter(Instruments.userid == user_id).first()
            message = TextSendMessage(text=my_instrument.message)

    elif messagetype == "group":

        profile = line_bot_api.get_profile(user_id)

        if db.session.query(Instruments).filter(Instruments.userid == user_id).first() == None:
            instruments = Instruments( event.source.group_id,user_id ,None ,None ,profile.picture_url)
            message = TextSendMessage(text="教えてくれてありがとう！\nよろしくね" + profile.display_name + "さん\n個人のほうで　自己紹介　って言ってみて")
            db.session.add(instruments)
            db.session.commit()
            
        elif usermessage == "問題":
                
            message = quiz(event)
        
        elif db.session.query(Instruments).filter(Instruments.userid == user_id).first() != None:
            instruments = db.session.query(Instruments).filter(Instruments.userid == user_id).first()
            instruments.groupid = event.source.group_id
            instruments.icon = profile.picture_url
            message = TextSendMessage(text="おっ、" + profile.display_name + "さんじゃないか\nこっちでもろしくね")
            db.session.add(instruments)
            db.session.commit()

    return message

def quiz(event):
    
    instruments = db.session.query(Instruments).filter(Instruments.status == "registed").all()
    quizmember = db.session.query(Instruments.userid).filter(Instruments.status == "registed").all()
    quizmembericon = db.session.query(Instruments.icon).filter(Instruments.status == "registed").all()
    
    count = len(instruments)
    num = random.randint(0 ,count - 1)
    answer = Answer(quizmember[num].userid)
    db.session.add(answer)
    db.session.commit()
    
    memberinstruments = db.session.query(Instruments).filter(Instruments.userid == quizmember[num].userid).first()
    
    contents = []
    
    for i in range(count):
        profile = line_bot_api.get_profile(quizmember[i].userid)
        quizmembername = profile.display_name
        item = QuickReplyButton(action=PostbackAction(label = quizmembername, display_text = quizmembername + "さん", data = quizmember[i].userid, imageUrl = quizmembericon[i].icon))
        contents.append(item)
    
    message = TextSendMessage(text = memberinstruments.message, quick_reply=QuickReply(items = contents))
    
    return message

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

@handler.add(PostbackEvent)
def postbackevent(event):
    answer = db.session.query(Answer).all()
    print(event.postback.data)
    print(answer[-1].answer)
    if event.postback.data == "retry":
        instruments = db.session.query(Instruments).filter(Instruments.userid == event.source.user_id).first()
        instruments.status = "registing"
        db.session.add(instruments)
        db.session.commit()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="もう一度自己紹介を入力してね")
            )
    elif event.postback.data == "ok":
        instruments = db.session.query(Instruments).filter(Instruments.userid == event.source.user_id).first()
        instruments.status = "registed"
        db.session.add(instruments)
        db.session.commit()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="登録しました")
            )
    elif event.postback.data == answer[-1].answer:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="正解！！！")
        )
    elif event.postback.data != answer[-1].answer:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="違うよ！！")
        )
        

        instruments = db.session.query(Instruments).filter(Instruments.status == "registed").all()
        quizmember = db.session.query(Instruments.userid).filter(Instruments.status == "registed").all()
        quizmembericon = db.session.query(Instruments.icon).filter(Instruments.status == "registed").all()
        
        count = len(instruments)
        
        memberinstruments = db.session.query(Instruments).filter(Instruments.userid == quizmember[num].userid).first()
        
        contents = []
        
        for i in range(count):
            profile = line_bot_api.get_profile(quizmember[i].userid)
            quizmembername = profile.display_name
            item = QuickReplyButton(action=PostbackAction(imageUrl = quizmembericon[i].icon, label = quizmembername, display_text = quizmembername + "さん", data = quizmember[i].userid))
            contents.append(item)
        
        message = TextSendMessage(text = memberinstruments.message, quick_reply=QuickReply(items = contents))

        line_bot_api.reply_message(
            event.reply_token,
            message
            )

@handler.add(FollowEvent)
def follow_event(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="こんにちは！")
        )


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message=event.message.text
    keywards = ["ゲーム","あいすぶいく", "アイスブレイク","げーむ"]
    save_starting_game(message)
    game = take_starting_game()
    group_id = event.source.group_id
    first_user = get_ranking(group_id)
    
    if game == "変顔":
        reply_message=TextSendMessage("画像を送ってね")
    elif game == "これ誰":
        reply_message = dealmessage(event)

	
    elif game == "正解探し":
        reply_message=TextSendMessage("「お題」って言ってね") #トリスト
    elif game in keywards:
        reply_message = TemplateSendMessage(
            "tempalte",
            CarouselTemplate(
                [
                    CarouselColumn(
                        thumbnail_image_url="https://ice-breake.herokuapp.com/static/yattinda.jpg",
                        title="変顔採点",
                        text=f"変顔を採点します\n普通の顔と変顔を送ってください\n１位 :{first_user}",
                        actions=[MessageAction("遊ぶ", "変顔")]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://rr.img.naver.jp/mig?src=http%3A%2F%2Fimgcc.naver.jp%2Fkaze%2Fmission%2FUSER%2F20140722%2F51%2F5551361%2F4%2F480x602xbb1ca7f0feef63f896500253.jpg%2F300%2F600&twidth=300&theight=600&qlt=80&res_format=jpg&op=r",
                        title="これだーれだ？",
                        text="botに個人チャットで自己紹介文を送ってください\nグループに紹介文が送られるので当ててください",
                        actions=[MessageAction("遊ぶ", "これ誰")]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://prtimes.jp/i/47616/5/resize/d47616-5-677884-3.jpg",
                        title="正解は何だ",
                        text="みんなで答えを探そう\n新たな発見があるはずだ",
                        actions=[MessageAction("遊ぶ", "正解探し")]
                    ),
                ]
            )
        )
    elif game == "やめる":
        save_starting_game("None")
        reply_message = TextSendMessage("ばいばーい")
        
    line_bot_api.reply_message(event.reply_token, reply_message)



@handler.add(JoinEvent)
def joinevent(event):
    game = take_starting_game()
    if game == "これ誰":
		group_id = event.source.group_id
    
    	line_bot_api.reply_message(
        	event.reply_token,
        	TextSendMessage(text="こんにちは！\n子のアカウントを追加してからみなさんの名前を教えてください")
        )

@handler.add(UnfollowEvent)
def unfollowevent(event):
    game = take_starting_game()
    if game == "これ誰":
    	if db.session.query(Instruments).filter(Instruments.userid == event.source.user_id).first() != None:

        	instruments = db.session.query(Instruments).filter(Instruments.userid == event.source.user_id).first()
        	instruments.groupid = None
        	instruments.userid = None
        	instruments.message = None
        	instruments.status = None
        	instruments.icon = None
        	db.session.add(instruments)
        	db.session.commit()
        
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

    
